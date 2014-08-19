#!/usr/bin/env python
# -*- coding: utf-8 -*-

#todaysdate = '2014-01-27'
#todaysfolder = "{0}{1}{2}_BC_SET_B".format(todaysdate[5:7],todaysdate[8:10],todaysdate[2:4])
#todaysParent = "{0}_{1}".format(todaysdate[5:7],todaysdate[:4])

#####################################################################################################################
# 1 # FTP Download zip file or files ################################################################################
#####################################################################################################################
import profile

class memoize:
    # from http://avinashv.net/2008/04/python-decorators-syntactic-sugar/
    def __init__(self, function):
        self.function = function
        self.memoized = {}

    def __call__(self, *args):
        try:
            return self.memoized[args]
        except KeyError:
            self.memoized[args] = self.function(*args)
            return self.memoized[args]


def formatted_delta_path(flag='csv',textext=None,textpre=None,daysrange=1):
    import datetime
    fivedirs = []
    fivecsvs = []
    nowobj = datetime.datetime.now()
    for day in xrange(daysrange):
        delta = datetime.timedelta(weeks=0, days=day, hours=12, minutes=50, seconds=600)
        nowdelta = nowobj - delta
        
        datedir = '{0}{1:%B%d}{2}'.format(textpre, nowdelta, textext)
        datecsv = '{0}{1:%Y-%m-%d}{2}'.format(textpre, nowdelta, textext)
        fivedirs.append(datedir)
        fivecsvs.append(datecsv)
    
    if flag == 'csv':
        return fivecsvs
    else:
        return fivedirs



@memoize
def styles_awaiting_return():
    import sqlalchemy
    
    mysql_engine_www = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
    connection = mysql_engine_www.connect()
    queryNotReturnedStyles = "SELECT colorstyle, send_dt from offshore_status WHERE return_dt is null"

    result = connection.execute(queryNotReturnedStyles)
    
    colorstyles_list = []
    batchdirs       = []
    for row in result:
        colorstyles_list.append(row['colorstyle'])
        if row['send_dt']:
            send_date = "{0:%B%d}".format(row['send_dt'])
            send_dates = 'Pick/ImagesToDo{0}_Done'.format(send_date)
            batchdirs.append(send_dates)
    connection.close()

    return set(sorted(colorstyles_list)),set(batchdirs)

@memoize
def get_batches_sent():
    import ftplib
    username   = "bf"
    password   = "B14300F"
    ftpurl     = "prepressoutsourcing.com"
    remotepath = str('Drop/')
    fullftp    = os.path.join(ftpurl, remotepath)


    ftp = ftplib.FTP(ftpurl, username, password)
    ftp.cwd(remotepath)
    sentbatches = []
    try:
        ftp.retrlines('NLST', sentbatches.append)
    except ftplib.error_perm, resp:
        if str(resp) == "550 No files found":
            print "No files in this directory"
        else:
            raise

    ftp.quit()
    return sorted(sentbatches)

@memoize
def ftp_download_all_files(returndir,remotepath):
    import ftplib
    import os,sys,re
    #colorstyle = filepath.split('/')[-1][:9]
    #if re.findall(regex_colorstyle, colorstyle):
    username   = "bf"
    password   = "B14300F"
    ftpurl     = "prepressoutsourcing.com"
    #remotepath = 'Pick/ImagesToDo' + str(sys.argv[1]) + '_Done'
    fullftp    = os.path.join(ftpurl, remotepath)
    #returndir = '/mnt/srv/media/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned'
    #
    ftp = ftplib.FTP(ftpurl)
    ftp.login(username, password)
    ftp.cwd(remotepath)

    filenames = []
    styles_not_downloaded, batch_list = styles_awaiting_return()
    try:
        ftp.retrlines('NLST', filenames.append)
    except ftplib.error_perm, resp:
        if str(resp) == "550 No files found":
            print "No files in this directory"
        else:
            raise
    
    ## if filenames is a dir decend into dirand list again till there are files found then dload or fo straught to dload
    if len(filenames) == 1:
        dname = filenames.pop()
        print dname
        if not re.findall(re.compile(r'^.+?\.[ZIziJPNGjpng]{3}$'), dname):
            ftp.cwd(dname)
    filenames = []
    ftp.retrlines('NLST', filenames.append)

    ##dload
    count = len(filenames)
    filtered_filenames = []
    for filename in filenames:
        if filename[:9] in styles_not_downloaded:
            filtered_filenames.append(filename)
    
    for filename in filtered_filenames:       
        local_filename = os.path.join(returndir,filename.lower().replace(' ',''))
        with open(local_filename, 'wb') as file:
            #remfile = os.path.join(str(batch) + '_Done', str(filename))
            #print remfile
            #ftp.cwd(remotepath)
            ftp.retrbinary('RETR '+ filename, file.write)
            count -= 1
            print "Successfully Retrieved--> At most, {0}\v{1} Files Remaining".format(filename,count)
        #file.close()
    ftp.close()


#####################################################################################################################
# 2 # Unzip downloaded file##########################################################################################
#####################################################################################################################

def unzip_dir_savefiles(zipin, extractdir):
    import zipfile,sys,datetime,os,re
    regex_png = re.compile(r'^[^\.].+?[jpng]{3}$')
    os.chdir(extractdir)
    # Open zip file
    zipf   = zipfile.ZipFile(zipin, 'r')
    
    # ZipFile.read returns the bytes contained in named file
    filenames = zipf.namelist()
    #print "777e3e3",os.path.abspath(os.curdir)
    for filename in filenames:
        if re.findall(regex_png, filename):    
            f = zipf.open(filename)
            contents = f.read()
            f.close()
            writefile = os.path.join(extractdir, filename.split('/')[-1])
            try:
                with open(writefile, 'w') as wfile:
                    wfile.write(contents)
                    print 'Extracting to --> {0}/{1}'.format(extractdir, filename.split('/')[-1])
            except IOError:
                print "IO Error -->{0}".format(filename)
                #os.rename(filename, filename.replace('2_Returned', 'X_Errors'))
                pass
    return zipin

#####################################################################################################################
# 3 and 4 # Magick Crop and save as 400x480 _m.jpg ##################################################################
#####################################################################################################################
@memoize
def subproc_magick_png(img, destdir, dimensions=None):
    import subprocess,re,os
    regex_coded = re.compile(r'^.+?/[1-9][0-9]{8}_[1-6]\.jpg$')
    regex_alt = re.compile(r'^.+?/[1-9][0-9]{8}_\w+?0[1-6]\.[JjPpNnGg]{3}$')
    regex_valid_style = re.compile(r'^.+?/[1-9][0-9]{8}_?.*?\.[JjPpNnGg]{3}$')

    if not destdir:
        destdir = '.'
    #imgdestpng_out = os.path.join(tmp_processing, os.path.basename(imgsrc_jpg))
    os.chdir(os.path.dirname(img))

    
    format = img.split('.')[-1]
    
    os.chdir(os.path.dirname(img))

    ## Destination name
    if not destdir:
        destdir = os.path.abspath('.')
    else:
        destdir = os.path.abspath(destdir)

    outfile = os.path.join(destdir, img.split('/')[-1].split('.')[0] + '.png')

    
    ## Get variable values for processing
    
    if not dimensions:
        dimensions = '100%'
        vert_horiz = '100%'

    subprocess.call([
            'convert',
            '-format',
            format,
            img,
            '-define',
            'png:preserve-colormap',
            '-define',
            'png:format\=png24',
            '-define',
            'png:compression-level\=N',
            '-define',
            'png:compression-strategy\=N',
            '-define',
            'png:compression-filter\=N',
            '-format',
            'png',
            "-define",
            "filter:blur=0.625",
            #"filter:blur=0.88549061701764",
            '-background',
            'white',
            '-gravity',
            'center',
            '-extent', 
            dimensions,
            "-colorspace",
            "sRGB",
            '-unsharp',
            '2x2.7+0.5+0',
            '-quality', 
            '95',
            os.path.join(destdir, img.split('/')[-1].split('.')[0] + '.png')
            ])
        
    print 'Done {}'.format(img)
    return os.path.join(destdir, img.split('/')[-1].split('.')[0] + '.png')

@memoize
def subproc_pad_to_x480(img,destdir):
    import subprocess, os

    start_time = time.time()

    fname = img.split("/")[-1].split('.')[0]  # .replace('_1','_m').lower()
    ext = img.split(".")[-1]
    outfile = os.path.join(destdir, fname + "_l.jpg")

    #try:
    subprocess.call([
        "convert",
        img,
        '-format',
        'jpg',
        # '-crop',
        # str(
        # subprocess.call(['convert', img, '-virtual-pixel', 'edge', '-blur', '0x15', '-fuzz', '1%', '-trim', '-format', '%wx%h%O', 'info:'], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False))
        # ,
        '-colorspace',
        'sRGB',
        # "-filter",
        # "LanczosSharp",
        # #        '-trim',
        # "-define",
        # "filter:blur=0.9891028367558475",
        "-distort",
        "Resize",
        "400x480",
        '-background',
        'white',
        #        '-gravity',
        #        'center',
        #        '-trim',
        #        '-gravity',
        #        'center',
        '-extent',
        "400x480",
        #        '+repage',
        #        '-background',
        #        'white',
        #        '+repage',
        '-colorspace',
        'sRGB',
        "-channel",
        "RGBA",
        "-unsharp",
        "2x0.5+0.5+0",
        '-quality',
        '100',
        #'-strip',
        outfile,
    ])

    end_time = time.time() - start_time
    print "{0}--- {1} seconds ---".format(outfile, end_time)
    return outfile

@memoize
def subproc_pad_to_x240(img,destdir):
    import subprocess, os

    start_time = time.time()

    fname = img.split("/")[-1].split('.')[0] #.replace('_1','_m').lower()
    ext = img.split(".")[-1]
    outfile = os.path.join(destdir, fname + "_m.jpg")

    #try:
    subprocess.call([
        "convert",
        img,
        '-format',
        'jpg',
        # '-crop',
        # str(
        # subprocess.call(['convert', img, '-virtual-pixel', 'edge', '-blur', '0x15', '-fuzz', '1%', '-trim', '-format', '%wx%h%O', 'info:'], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False))
        # ,
        '-colorspace',
        'sRGB',
        # "-filter",
        # "Spline",
        # "-filter",
        # "Cosine",
        # "-filter",
        # "LanczosSharp",
        # #        '-trim',
        # "-define",
        # "filter:blur=0.9891028367558475",
        "-distort",
        "Resize",
        "300x360",
        '-background',
        'white',
        #        '-gravity',
        #        'center',
        #        '-trim',
        #        '-gravity',
        #        'center',
        '-extent',
        "300x360",
        #        '+repage',
        #        '-background',
        #        'white',
        #        '+repage',
        '-colorspace',
        'sRGB',
        "-channel",
        "RGBA",
        "-unsharp",
        "2x0.5+0.5+0",
        '-quality',
        '100',
        #'-strip',
        outfile,
    ])
    #except IOError:
    #    print "Failed: {0}".format(outfile)

    end_time = time.time() - start_time
    print "{0}--- {1} seconds ---".format(outfile, end_time)
    return outfile

###########################################################################
@memoize
def subproc_multithumbs_4_2(filepath,destdir):
    import subprocess, os

    fname = filepath.split("/")[-1].split('.')[0] #.lower().replace('_1.','.').replace('_1','')
    ext = filepath.split(".")[-1]

    outfile_l = os.path.join(destdir, fname + "_l.jpg")
    outfile_m = os.path.join(destdir, fname + "_m.jpg")

    subprocess.call([
        'convert',
        filepath,
        '-format',
        ext,
        #'-crop',
        # str(
        # subprocess.call(['convert', filepath, '-virtual-pixel', 'edge', '-blur', '0x15', '-fuzz', '1%', '-trim', '-format', '%wx%h%O', 'info:'], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False))
        # ,
        # '-gravity',
        #  'center',
        # '-trim',
        # '-colorspace',
        # 'LAB',
        #"-filter",
        #"LanczosSharp",
        '-write',
        'mpr:copy-of-original',
        #'+delete',
            ## Begin generating imgs
            # --> Large Jpeg
            'mpr:copy-of-original',
            '-format',
            'jpg',
            '-resize',
            '400x480',
            #'-gravity',
            #'center',
            # '-background',
            # 'white',
            # '-extent',
            # '400x480',
            '-colorspace',
            'sRGB',
            '-unsharp',
            '2x0.5+0.5+0',
            '-quality',
            '95',
            '-write',
            outfile_l,
            #'+delete',

            ## Medium Jpeg
            'mpr:copy-of-original',
            '-format',
            'jpg',
            '-resize',
            '300x360',
            #'-gravity',
            #'center',
            # '-background',
            # 'white',
            # '-extent',
            # '300x360',
            '-colorspace',
            'sRGB',
            '-unsharp',
            '2x0.5+0.5+0',
            '-quality',
            '95',
            '-write',
            outfile_m,
            #'+delete',
            'null:',
    ])
    end_time = time.time() - start_time
    print "{0}--- {1} seconds ---".format(outfile_m, end_time)

    #return

##########################################
# 5 # Upload stripped bg _m.jpg files to ImageDrop ##################################################################
#####################################################################################################################
##### Upload tmp_loading dir to imagedrop via FTP using Pycurl  #####
@memoize
def pycurl_upload_imagedrop(img):
    import pycurl, os
    #import FileReader
    localFilePath = os.path.abspath(img)
    localFileName = localFilePath.split('/')[-1]

    mediaType = "8"
    ftpURL = "ftp://file3.bluefly.corp/ImageDrop/"
    ftpFilePath = os.path.join(ftpURL, localFileName)
    ftpUSERPWD = "imagedrop:imagedrop0"

    if localFilePath != "" and ftpFilePath != "":
        ## Create send data

        ### Send the request to Edgecast
        c = pycurl.Curl()
        c.setopt(pycurl.URL, ftpFilePath)
        #c.setopt(pycurl.PORT , 21)
        c.setopt(pycurl.USERPWD, ftpUSERPWD)
        #c.setopt(pycurl.VERBOSE, 1)
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 8)
        c.setopt(c.FAILONERROR, True)
        #c.setopt(pycurl.FORBID_REUSE, 1)
        #c.setopt(pycurl.FRESH_CONNECT, 1)
        f = open(localFilePath, 'rb')
        c.setopt(pycurl.INFILE, f)
        c.setopt(pycurl.INFILESIZE, os.path.getsize(localFilePath))
        c.setopt(pycurl.INFILESIZE_LARGE, os.path.getsize(localFilePath))
        #c.setopt(pycurl.READFUNCTION, f.read());
        #c.setopt(pycurl.READDATA, f.read());
        c.setopt(pycurl.UPLOAD, 1L)

        try:
            c.perform()
            c.close()
            print "Successfully Uploaded --> {0}".format(localFileName)
            ## return 200
        except pycurl.error, error:
            errno, errstr = error
            print 'An error occurred: ', errstr
            try:
                c.close()
            except:
                print "Couldnt Close Cnx"
                pass
            return errno

#####
def upload_imagedrop(root_dir, destdir=None):
    import os, sys, re, csv, shutil, glob
    ## Make the success and fail dirs
    regex_png = re.compile(r'^.*?\.png$')
    archive_uploaded = os.path.join(root_dir, 'uploaded')
    tmp_failed = os.path.join(root_dir, 'failed_upload')
    try:
        os.makedirs(archive_uploaded, 16877)
    except:
        pass

    try:
        os.makedirs(tmp_failed, 16877)
    except:
        pass


    import time
    #### UPLOAD upload_file via ftp to imagedrop using Pycurl

    upload_tmp_loading = glob.glob(os.path.join(root_dir, '*.*g'))
    for upload_file in upload_tmp_loading:
        #### UPLOAD upload_file via ftp to imagedrop using Pycurl
        ## Then rm loading tmp dir
        dst_file = upload_file.replace(os.path.dirname(upload_file).split('/')[-1],
                                       os.path.dirname(upload_file).split('/')[-1][0] + '/uploaded/')
        failed = upload_file.replace(os.path.dirname(upload_file).split('/')[-1],
                                       os.path.dirname(upload_file).split('/')[-1][0] + '/failed_upload/')
        try:
            code = pycurl_upload_imagedrop(upload_file)
            if code == '200':
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                if regex_png.findall(upload_file):
                    shutil.move(upload_file, destdir)
                else:
                    shutil.move(upload_file, archive_uploaded)
                print "1stTryOK"
            elif code:
                print code, upload_file
                time.sleep(float(.3))
                try:
                    pycurl_upload_imagedrop(upload_file)
                    print "Uploaded {}".format(upload_file)
                    time.sleep(float(.3))
                    shutil.move(upload_file, archive_uploaded)
                except:
                    if os.path.exists(failed):
                        os.remove(failed)
                    shutil.move(upload_file, tmp_failed)
                    pass
            else:
                print "Uploaded {}".format(upload_file)
                time.sleep(float(.3))
                final = dst_file #upload_file.replace('/3_ListPage_to_Load/','/3_ListPage_to_Load/uploaded/')
                if os.path.exists(final):
                    os.remove(final)
                shutil.move(upload_file, archive_uploaded)
        except OSError:
            print "Error moving Finals to Arch {}".format(file)
            if os.path.exists(failed):
                os.remove(failed)
            shutil.move(upload_file, tmp_failed)
            pass

    try:
        archglob =  glob.glob(os.path.join(archive_uploaded, '*.png'))
        if os.path.isdir(destdir):
            finaldir = os.path.abspath(destdir)
            for f in archglob:
                try:
                    final = os.path.join(finaldir, f.split('/')[-1]) #f.replace(os.path.dirname(upload_file).split('/')[-1],)  #'/3_ListPage_to_Load/','/3_ListPage_to_Load/uploaded/')
                    if os.path.exists(final):
                        os.remove(final)
                        shutil.move(f, finaldir)
                except:
                    pass
        else:
            return archglob
    except:
        pass
        return 'NOARCHGLOB'

#####################################################################################################################
# 7 # After Upload set return_dt on offshore_status #################################################################
#####################################################################################################################
@memoize
def sqlQuery_set_returndt(style):
    import sqlalchemy, datetime
    todaysdate_returndt = str(datetime.date.today())
    mysql_engine_www = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
    connection = mysql_engine_www.connect()
    try:
        sql = "UPDATE offshore_status SET return_dt='{0}' WHERE colorstyle='{1}' AND return_dt is null".format(todaysdate_returndt, style)
        connection.execute(sql)
        # connection.execute("""
        #         UPDATE offshore_status (colorstyle)
        #         VALUES (%s)
        #         SET return_dt=DATE_FORMAT(NOW(),'%Y-%m-%d');
        #         """, style)
    except sqlalchemy.exc.IntegrityError:
        print "Duplicate Entry {0}".format(style)
    connection.close()
#####################################################################################################################
## 8 ## Write styles to clear to csv, which will be use to Clear List page cdn with edgecast and style number, no version needed on List page for now
#####################################################################################################################
def csv_write_datedCacheClearList(styleslist, destdir=None):
    import csv,datetime,os
    dt = str(datetime.datetime.now())
    today = dt.split(' ')[0]
    if not destdir:
        destdir = os.path.expanduser('~')
    f = os.path.join(destdir, today + '_clearedgecast.csv')
    with open(f, 'ab+') as csvwritefile:
        writer = csv.writer(csvwritefile, delimiter='\n', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        for line in styleslist:
            try:
                writer.writerow([line])
            except IndexError():
                pass

###########################
### Not used Currently
###########################
def edgecast_clear_primary_only(colorstyle):
    import pycurl,json,sys,os
    token = "9af6d09a-1250-4766-85bd-29cebf1c984f"
    account = "4936"
    mediaPath = "http://cdn.is.bluefly.com/mgen/Bluefly/prodImage.ms?productCode={0}&width=251&height=300".format(colorstyle)
    mediaType = "8"
    purgeURL = "https://api.edgecast.com/v2/mcc/customers/{0}/edge/purge".format(account)
    if token != "" and account != "" and mediaPath != "" and mediaType != "":
        ## Create send data
        data = json.dumps({
        'MediaPath' : mediaPath,
        'MediaType' : mediaType 
        })
        #data = json_encode(request_params)
        head_authtoken = "Authorization: tok:{0}".format(token)
        head_content_len= "Content-length: {0}".format(str(len(data)))
        head_accept = 'Accept: application/json'
        head_contenttype = 'Content-Type: application/json'

        c = pycurl.Curl()
        c.setopt(pycurl.URL, purgeURL)
        c.setopt(pycurl.PORT , 443)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.HEADER, 0)
        #c.setopt(pycurl.INFOTYPE_HEADER_OUT, 1)
        #c.setopt(pycurl.RETURNTRANSFER, 1)
        c.setopt(pycurl.FORBID_REUSE, 1)
        c.setopt(pycurl.FRESH_CONNECT, 1)
        c.setopt(pycurl.CUSTOMREQUEST, "PUT")
        c.setopt(pycurl.POSTFIELDS,data)
        c.setopt(pycurl.HTTPHEADER, [head_authtoken, head_contenttype, head_accept, head_content_len])
        try:
            c.perform()
            c.close()
            print "Successfully Sent Purge Request for --> {0}".format(mediaPath)
        except pycurl.error, error:
            errno, errstr = error
            print 'An error occurred: ', errstr

#####################################################################################################################
## RUN ##
######### find out how many zips dloaded then extract pngs from zip
import timeit

@memoize
def main():
    import glob,ftplib,sys,datetime,os,re,shutil, time
    print time.strftime('%M%S')
    print 'START'
    st = time.time()
    regex_zipfilename = re.compile(r'^[^\.].+?[zipZIP]{3}$')
    regex_zipfilepath = re.compile(r'^/.+?[zipZIP]{3}$')

    todaysdate = str(datetime.date.today())

    #todaysnow = "{0:%Y%m%d_%f}".format(str(datetime.datetime.now()))
    todaysnow = time.strftime('%Y%m%d-%H%M%s')

    returndir           = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned' + todaysnow
    listpagedir         = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/3_ListPage_to_Load' + todaysnow
    archdir             = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive'
    archdirpng          = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/PNG'
    errordir            = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/X_Errors'
    uploaded_jpgs_arch  = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/JPG/LIST_PAGE_LOADED'
    pathed_jpgs_arch    = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/JPG'

    ##TODO: This is a terrible workaround for deleting the entire dir at the end of this instead of just the files, but no harm no foul, just ugly
    try:
        os.makedirs(returndir)
    except:
        pass

    try:
        os.makedirs(listpagedir)
    except:
        pass

    #####################################################################################################################
    # 1 #  Download all files on remote dir via FTP trying dates within 5 day range
    #####################################################################################################################
    
    remotepaths = formatted_delta_path(flag='ftpdirs', daysrange=4, textpre='Pick/ImagesToDo', textext='_Done')
    
    for remotepath in remotepaths:
        try:
            ftp_download_all_files(returndir,remotepath)
        except ftplib.error_perm:
            pass

    #####################################################################################################################
    # 3 # After unzip of complete PNGs Archive and Create new List page image
    #####################################################################################################################
    ## Get all extracted PNGs and rename with _1 ext and move to archive dir 4, then copy/create _m.jpg in 3_ListPage_to_Load
    parentdir = ''
    returned_files = []
    edgecast_clear_list = []
    print time.strftime('%M%S')

    globreturned = glob.glob(os.path.join(returndir, '*.??g'))
    count = len(globreturned)
    total = count
    for f in globreturned:
        returned_files.append(os.path.abspath(f))
        count -= 1
        print "Successfully Extracted--> {0}\v{1} Files Remaining".format(f,count)
        edgecast_clear_list.append(os.path.abspath(f))

    edgecast_clear_list = list(sorted(set(edgecast_clear_list)))
    count = len(returned_files)
    while len(returned_files) >= 1:
        img        = os.path.abspath(returned_files.pop())
        parentdir          = os.path.dirname(img)
        filename           = img.split('/')[-1]
        colorstyle         = img.split('/')[-1].split('.')[0]
        pngarchived_dirname = os.path.dirname(img).replace('2_Returned','4_Archive/PNG')
        pngarchived_fname  = img.split('/')[-1].replace('.png', '_1.png')
        pngarchived_fname  = img.split('/')[-1].replace('.jpg', '_1.jpg')
        pngarchived_path   = os.path.join(pngarchived_dirname, pngarchived_fname)
        jpgarchivepath     = os.path.join(pathed_jpgs_arch,filename)

        try:
            os.makedirs(pngarchived_dirname)
        except:
            print "Failed makedirs"

        #else:
        count -= 1
        print "Creating Jpgs for--> {0}\v{1} Files Remaining".format(img,count)
        #subproc_multithumbs_4_2(pngarchived_path,listpagedir)
        hires_zoom = subproc_magick_png(img,listpagedir)
        if os.path.isfile(hires_zoom):
            if os.path.isfile(jpgarchivepath):
                os.remove(jpgarchivepath)
                shutil.move(img, jpgarchivepath)
            else:
                shutil.move(img, jpgarchivepath)
        subproc_pad_to_x480(hires_zoom,listpagedir)
        subproc_pad_to_x240(hires_zoom,listpagedir)
        shutil.copy(hires_zoom, pngarchived_path) #os.path.join(listpagedir, filename))

    ## Remove empty dir after padding etc
    if parentdir:
        if len(os.listdir(parentdir)) == 0: os.rmdir(parentdir)


    #####################################################################################################################
    # 5 # NEW Upload all  _m.jpg @ 400x480 located in the 3_LisPage... folder
    #####################################################################################################################
    import os, sys, re, csv, shutil, glob
    bgremoved_toload = []
    import time, ftplib

    upload_imagedrop(listpagedir,destdir=archdirpng)

    #for f in loadfiles:
    #    bgremoved_toload.append(os.path.abspath(f))

    ### 5a ## Move the copy of the png from the LIST PAGE LOADED dir used only to upload, stored as _1.png

    # try:
    #     os.makedirs(archivedir)
    # except:
    #     print "Failed makedirs for Archiving"

    ## Build list  and move files to archive and update DB
    import shutil

    # if type(success) == list:
    #     globreturned = success
    #     for f in globreturned:
    #         shutil.move(f, uploaded_jpgs_arch)
    # else:

    globreturned = glob.glob(os.path.join(listpagedir, 'uploaded/*_l.jpg'))

    # globreturned = glob.glob(os.path.join(pngarchived_dirname, '*.png'))

    end = time.time()
    print end - st
    print time.strftime('%M%S')
    print 'LOADED'
    count = len(globreturned)
    for f in globreturned:
        colorstyle = os.path.abspath(f).split('/')[-1][:9]
        print f + " is file ",colorstyle + ' SQLRETURN'
    #    try:
    #        shutil.move(f, archivedir)
    #        count -= 1
    #        print "Successfully Archived--> {0}\v{1} Files Remaining".format(f,count)
    #
    #    except shutil.Error:
    #        os.rename(f, os.path.join(archivedir, f.split('/')[-1]))

        #####################################################
        # 7 # Update offshore_status with todays date as sent
        #####################################################
        try:
            sqlQuery_set_returndt(colorstyle)
            print "SQLRETUrN {}".format(colorstyle)
        except:
            print "Failed Entrering Return dt for --> {0}".format(colorstyle)
        #####################################################
        #####################################################
        # try:
        #
        #     #edgecast_clear_primary_only(colorstyle)
        # except:
        #     pass

    ### 8ish ## Write styles to Clear at end of day through separate Edgecast script
    cacheclear_csvarch  = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/CSV'
    print edgecast_clear_list

    toclear = [ fname[:].split('/')[-1][:9] for fname in edgecast_clear_list ]
    csv_write_datedCacheClearList(toclear, destdir=cacheclear_csvarch)

    ### For now copy all png in error dir to my DropFinalFiles only dir which will create and load in reg processing scripts
    # for f in glob.glob(os.path.join(errordir, '*.png')):
    #     try:
    #         shutil.copy(f, '/mnt/Post_Complete/Complete_to_Load/Drop_FinalFilesOnly/JohnBragato')
    #     except:
    #         pass

    ## finally delete the zip file from the return dir
    # for f in glob.glob(os.path.join(returndir, '*/*.?[a-zA-Z][a-zA-Z][a-zA-Z]')):
    #     if os.path.isfile(f):
    #         os.remove(os.path.abspath(f))
    #     elif os.path.isdir(f):
    #         pass
    # # Delete Dirs
    shutil.rmtree(os.path.abspath(listpagedir))

    try:
        shutil.rmtree(os.path.abspath(returndir))
    except:
        pass
    return total

def test():
    main()
    L = []
    for i in range(100):
        L.append(i)

import time
start_time = time.time()
total = main()
end_time = time.time() - start_time
avg_time = end_time/total
print "Total--- {0} seconds --- \n{1} sec. Avg per Style".format(end_time,avg_time)

#

# if __name__ == '__main__':
#     import timeit
#     print timeit.timeit("test()", setup="from __main__ import test"))
