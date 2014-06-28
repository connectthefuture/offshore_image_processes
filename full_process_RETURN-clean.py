#!/usr/bin/env python
# -*- coding: utf-8 -*-

#todaysdate = '2014-01-27'
#todaysfolder = "{0}{1}{2}_BC_SET_B".format(todaysdate[5:7],todaysdate[8:10],todaysdate[2:4])
#todaysParent = "{0}_{1}".format(todaysdate[5:7],todaysdate[:4])

#####################################################################################################################
# 1 # FTP Download zip file or files ################################################################################
#####################################################################################################################

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

def ftp_download_allzips(returndir):
    import ftplib
    import os,sys,re
    #colorstyle = filepath.split('/')[-1][:9]
    #if re.findall(regex_colorstyle, colorstyle):
    username   = "bf"
    password   = "B14300F"
    ftpurl     = "prepressoutsourcing.com"
    remotepath = 'Pick/ImagesToDo' + str(sys.argv[1]) + '_Done'
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

    ## dload
    count = len(filenames)
    filtered_filenames = []
    for filename in filenames:
        if filename[:9] in styles_not_downloaded:
            filtered_filenames.append(filename)
    
    for filename in filtered_filenames:       
        local_filename = os.path.join(returndir,filename.lower().replace(' ',''))
        with open(local_filename, 'wb') as file:
            # remfile = os.path.join(str(batch) + '_Done', str(filename))
            # print remfile
            # ftp.cwd(remotepath)
            ftp.retrbinary('RETR '+ filename, file.write)
            count -= 1
            print "Successfully Retrieved--> At most, {0}\v{1} Files Remaining".format(filename,count)
    ftp.close()


#####################################################################################################################
# 3 and 4 # Magick Crop and save as 400x480 _m.jpg ##################################################################
#####################################################################################################################

def subproc_pad_to_x480(file,destdir):
    import subprocess, os
    
    fname = file.split("/")[-1].split('.')[0].replace('_1','_l').lower()
    ext = file.split(".")[-1]
    outfile = os.path.join(destdir, fname + ".jpg")    
    subprocess.call([
        "convert", 
        file, 
        '-format', 
        'jpg',
        '-colorspace',
        'LAB',
        "-filter",
        "LanczosSharp",
        #        '-trim', 
        '-resize',
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
        #        "-unsharp", 
        #        "0x0.75+0.75+0.008",
        '-quality',
        '100',
        #'-strip', 
        outfile,
    ])
    #except IOError:
    #    print "Failed: {0}".format(outfile)
    return outfile


def subproc_pad_to_x240(file,destdir):
    import subprocess, os
    
    fname = file.split("/")[-1].split('.')[0].replace('_1','_m').lower()
    ext = file.split(".")[-1]
    outfile = os.path.join(destdir, fname + ".jpg")    
    
    #try:            
    subprocess.call([
        "convert", 
        file, 
        '-format', 
        'jpg',
        # '-crop',
        # str(
        # subprocess.call(['convert', file, '-virtual-pixel', 'edge', '-blur', '0x15', '-fuzz', '1%', '-trim', '-format', '%wx%h%O', 'info:'], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False))
        # ,
        '-colorspace',
        'LAB',
        "-filter",
        "LanczosSharp",
        #        '-trim', 
        '-resize',
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
    return outfile

###########################################################################
# 5 # Upload stripped bg _m.jpg files to ImageDrop ##################################################################
#####################################################################################################################
def upload_to_imagedrop(file):
    import ftplib
    session = ftplib.FTP('file3.bluefly.corp', 'imagedrop', 'imagedrop0')
    fileread = open(file, 'rb')
    filename = str(file.split('/')[-1])
    session.cwd("ImageDrop/")
    session.storbinary('STOR ' + filename, fileread, 8*1024)
    fileread.close()
    session.quit() 

##
##### Upload tmp_loading dir to imagedrop via FTP using Pycurl  #####
def pycurl_upload_imagedrop(img):
    import pycurl, os
    # import FileReader
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
        # c.setopt(pycurl.PORT , 21)
        c.setopt(pycurl.USERPWD, ftpUSERPWD)
        # c.setopt(pycurl.VERBOSE, 1)
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 8)
        c.setopt(c.FAILONERROR, True)
        # c.setopt(pycurl.FORBID_REUSE, 1)
        # c.setopt(pycurl.FRESH_CONNECT, 1)
        f = open(localFilePath, 'rb')
        c.setopt(pycurl.INFILE, f)
        c.setopt(pycurl.INFILESIZE, os.path.getsize(localFilePath))
        c.setopt(pycurl.INFILESIZE_LARGE, os.path.getsize(localFilePath))
        # c.setopt(pycurl.READFUNCTION, f.read());        
        # c.setopt(pycurl.READDATA, f.read()); 
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
        try:
            code = pycurl_upload_imagedrop(upload_file)
            if code == '200':
                dst_file = upload_file.replace('/3_ListPage_to_Load/','/3_ListPage_to_Load/uploaded/')
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.move(upload_file, archive_uploaded)
                print "1stTryOK"
            elif code:
                print code, upload_file
                time.sleep(float(.3))
                try:
                    ftpload_to_imagedrop(upload_file)
                    print "Uploaded {}".format(upload_file)
                    time.sleep(float(.3))
                    shutil.move(upload_file, archive_uploaded)
                except:
                    failed = upload_file.replace('/3_ListPage_to_Load/','/3_ListPage_to_Load/failed_upload/')
                    if os.path.exists(failed):
                        os.remove(failed)
                    shutil.move(upload_file, tmp_failed)
                    pass
            else:
                print "Uploaded {}".format(upload_file)
                time.sleep(float(.3))
                final = upload_file.replace('/3_ListPage_to_Load/','/3_ListPage_to_Load/uploaded/')
                if os.path.exists(final):
                    os.remove(final)
                shutil.move(upload_file, archive_uploaded)
        except OSError:
            print "Error moving Finals to Arch {}".format(file)
            failed = upload_file.replace('/3_ListPage_to_Load/','/3_ListPage_to_Load/failed_upload/')
            if os.path.exists(failed):
                os.remove(failed)
            shutil.move(upload_file, tmp_failed)
            pass

    try:
        archglob =  glob.glob(os.path.join(archive_uploaded, '*.*g'))
        if os.path.isdir(destdir):
            finaldir = os.path.abspath(destdir)
            for f in archglob:
                try:
                    final = f.replace('/3_ListPage_to_Load/','/3_ListPage_to_Load/uploaded/')
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
import glob,zipfile,sys,datetime,os,re,shutil

regex_zipfilename = re.compile(r'^[^\.].+?[zipZIP]{3}$')
regex_zipfilepath = re.compile(r'^/.+?[zipZIP]{3}$')

todaysdate = str(datetime.date.today())

returndir    = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned'
listpagedir  = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/3_ListPage_to_Load'
archdir      = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive'
errordir     = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/X_Errors'

##TODO: This is a terrible workaround for deleting the entire dir at the end of this instead of just the files, but no harm no foul, just ugly
try:
    os.makedirs(returndir)
except:
    pass

#####################################################################################################################
# 1 #  Download all zips on remote dir via FTP
#####################################################################################################################

ftp_download_allzips(returndir)

  

#####################################################################################################################
# 3 # After unzip of complete PNGs Archive and Create new List page image
#####################################################################################################################
## Get all extracted PNGs and rename with _1 ext and move to archive dir 4, then copy/create _m.jpg in 3_ListPage_to_Load
parentdir = ''
returned_files = []
edgecast_clear_list = []

globreturned = glob.glob(os.path.join(returndir, '*.png'))
count = len(globreturned)
for f in globreturned:
    returned_files.append(os.path.abspath(f))
    count -= 1
    print "Successfully Extracted--> {0}\v{1} Files Remaining".format(f,count)
    edgecast_clear_list.append(os.path.abspath(f))

edgecast_clear_list = list(sorted(set(edgecast_clear_list)))
count = len(returned_files)
while len(returned_files) >= 1:
    strippedpng        = os.path.abspath(returned_files.pop())
    parentdir          = os.path.dirname(strippedpng)
    filename           = strippedpng.split('/')[-1]
    colorstyle         = strippedpng.split('/')[-1].split('.')[0]
    pngarchived_dirname = os.path.dirname(strippedpng).replace('2_Returned','4_Archive/PNG')
    pngarchived_fname  = strippedpng.split('/')[-1].replace('.png', '_1.png')
    pngarchived_path   = os.path.join(pngarchived_dirname, pngarchived_fname)
    
    try:
        os.makedirs(pngarchived_dirname)
    except:
        print "Failed makedirs"

    if os.path.isfile(pngarchived_path):
        pass
    else:
        shutil.move(strippedpng, pngarchived_path)
        count -= 1
        print "Creating Jpgs for--> {0}\v{1} Files Remaining".format(strippedpng,count)
        #subproc_multithumbs_4_2(pngarchived_path,listpagedir)
        subproc_pad_to_x480(pngarchived_path,listpagedir)
        subproc_pad_to_x240(pngarchived_path,listpagedir)
        shutil.copy(pngarchived_path, os.path.join(listpagedir, filename))
## Remove empty dir after padding etc
if parentdir:
    if len(os.listdir(parentdir)) == 0: os.rmdir(parentdir)


#####################################################################################################################
# 5 # NEW Upload all located in the 3_LisPage... folder
#####################################################################################################################
import os, sys, re, csv, shutil, glob
bgremoved_toload = []
import time, ftplib

success = upload_imagedrop(listpagedir)
print 'SUCCESS {}'.format(len(success))
#for f in loadfiles:
#    bgremoved_toload.append(os.path.abspath(f))

### 5a ## Move the copy of the png from the LIST PAGE LOADED dir used only to upload, stored as _1.png
uploaded_jpgs_arch  = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/JPG/LIST_PAGE_LOADED'

# try:
#     os.makedirs(archivedir)
# except:
#     print "Failed makedirs for Archiving"

## Build list  and move files to archive and update DB
import shutil

if type(success) == list:
    globreturned = success
    for f in globreturned:
        shutil.move(f, uploaded_jpgs_arch)
else:
    globreturned = glob.glob(os.path.join(uploaded_jpgs_arch, '*_l.jpg'))


count = len(globreturned)
for f in globreturned:
    colorstyle = f.split('/')[-1][:9]
    print 'COLORSTYLE {}'.format(colorstyle)
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
for f in glob.glob(os.path.join(returndir, '*/*.?[a-zA-Z][a-zA-Z][a-zA-Z]')):
    if os.path.isfile(f):
        os.remove(os.path.abspath(f))
    elif os.path.isdir(f):
        pass
        #shutil.rmtree(os.path.abspath(f))


######################################################################################################################
# ## 2 # After download list zip files dloaded and unzip
# #######################################################################################################################
# ### Grab all downloaded zips in a list prior to extracting pngs
# zipfiles_dload = []
# count = len(glob.glob(os.path.join(returndir, '*.zip')))
# for z in glob.glob(os.path.join(returndir, '*.zip')):
#     zipfiles_dload.append(os.path.abspath(z))
#     count -= 1
#     print "Successfully Downloaded--> {0}\v{1} Files Remaining".format(z,count)
# #
# ### unzip or pass if no zip exists 
# if len(zipfiles_dload) > 0:
#     while len(zipfiles_dload) >= 1:
#         zipreturned = os.path.abspath(zipfiles_dload.pop())
#         parentdir   = os.path.dirname(zipreturned)
#         zipname     = zipreturned.split('/')[-1].split('.')[0]
#         extractdir  = os.path.join(parentdir, zipname)
        
#         ## Make new dir named as zipfile name without ext to extract zip contents to
#         try:
#             os.mkdir(extractdir)
#         except:# SystemError:
#             pass
        
#         if os.path.isfile(zipreturned):
#             print "ZZZ",zipreturned, extractdir, zipname
#             unzip_dir_savefiles(zipreturned, extractdir)
#             os.remove(zipreturned)
  

#####################################################################################################################
# 2 # Unzip downloaded file##########################################################################################
#####################################################################################################################

# def unzip_dir_savefiles(zipin, extractdir):
#     import zipfile,sys,datetime,os,re
#     regex_png = re.compile(r'^[^\.].+?[png]{3}$')
#     os.chdir(extractdir)
#     # Open zip file
#     zipf   = zipfile.ZipFile(zipin, 'r')
    
#     # ZipFile.read returns the bytes contained in named file
#     filenames = zipf.namelist()
#     #print "777e3e3",os.path.abspath(os.curdir)
#     for filename in filenames:
#         if re.findall(regex_png, filename):    
#             f = zipf.open(filename)
#             contents = f.read()
#             f.close()
#             writefile = os.path.join(extractdir, filename.split('/')[-1])
#             try:
#                 with open(writefile, 'w') as wfile:
#                     wfile.write(contents)
#                     print 'Extracting to --> {0}/{1}'.format(extractdir, filename.split('/')[-1])
#             except IOError:
#                 print "IO Error -->{0}".format(filename)
#                 #os.rename(filename, filename.replace('2_Returned', 'X_Errors'))
#                 pass
#     return zipin

# def ftp_download_allzips(returndir):
#     import ftplib, datetime
#     import os,sys,re
#     #colorstyle = filepath.split('/')[-1][:9]
#     #if re.findall(regex_colorstyle, colorstyle):
#     username   = "bf"
#     password   = "B14300F"
#     ftpurl     = "prepressoutsourcing.com"
#     #remotepath = 'Pick/ImagesToDo_Done'
#     #todaysdate_senddt = "ImagesToDo{0:%B%d}_Done".format(datetime.date.today())
#     #remotepath = str('Pick/ImagesToDo' + todaysdate_senddt)
#     sent_batches = get_batches_sent()

#     styles_not_downloaded, batch_list = styles_awaiting_return()
#     sent_set = []
#     [ sent_set.append(f.split('/')[-1].strip('_Done')) for f in batch_list ]
#     batches_to_get = set(sent_set) | set(sent_batches)
#     filenames = []        
#     for batch in batches_to_get:
#         remotepath = os.path.join('Pick', str(batch) + '_Done') ##sys.argv[1])
#         fullftp    = os.path.join(ftpurl, remotepath)
#         #returndir = '/mnt/srv/media/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned'
#         #
#         ftp = ftplib.FTP(ftpurl)
#         ftp.login(username, password)
#         try:
#             ftp.cwd(remotepath)
#             ftp.retrlines('NLST', filenames.append)
#         except ftplib.error_perm, resp:
#             if str(resp) == "550 No files found":
#                 print "No files in this directory"
#             else:
#                 pass #raise
    
#     ## if filenames is a dir decend into dirand list again till there are files found then dload or fo straught to dload
#     # if len(filenames) == 1:
#     #     dname = filenames.pop()
#     #     print dname
#     #     if not re.findall(re.compile(r'^.+?\.[ZIziJPNGjpng]{3}$'), dname):
#     #         ftp.cwd(dname)
#     #filenames = []
#     #ftp.retrlines('NLST', filenames.append)

#     ##dload
#     count = len(filenames)
#     for filename in filenames:
#         if filename[:9] in styles_not_downloaded:
#             local_filename = os.path.join(returndir,filename.lower().replace(' ',''))
#             file = open(local_filename, 'wb')
#             for batch in batches_to_get:
#                 try:
#                     remfile = os.path.join(str(batch) + '_Done', str(filename))
#                     print remfile
#                     ftp.retrbinary('RETR '+ remfile, file.write)
#                     count -= 1
#                     print "Successfully Retrieved--> At most, {0}\v{1} Files Remaining".format(filename,count)
#                 except:
#                     pass
#             file.close()
#     ftp.close()


#####################################################################################################################
# 4 # Generate new list page jpgs, _m.jpg @ 400x480 from PNGs located in the 3_LisPage... folder
#####################################################################################################################
#import subprocess
#
#pngs_for_listpage_jpg = []
#for f in glob.glob(os.path.join(listpagedir, '*/*.png')):
#    pngs_for_listpage_jpg.append(os.path.abspath(f))
#
#for png in pngs_for_listpage_jpg:
#    magick_crop_saveX480(png)

# def subproc_multithumbs_4_2(filepath,destdir):
#     import subprocess, os
    
#     fname = filepath.split("/")[-1].split('.')[0].lower().replace('_1.','.').replace('_1','')
#     ext = filepath.split(".")[-1]
 
#     outfile_l = os.path.join(destdir, fname + "_l.jpg")    
#     outfile_m = os.path.join(destdir, fname + "_m.jpg")

#     subprocess.call([
#         'convert', 
#         filepath, 
#         '-format', 
#         ext,
#         #'-crop',
#         # str(
#         # subprocess.call(['convert', filepath, '-virtual-pixel', 'edge', '-blur', '0x15', '-fuzz', '1%', '-trim', '-format', '%wx%h%O', 'info:'], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False))
#         # ,
#         # '-gravity',
#         #  'center',
#         # '-trim',
#         # '-colorspace',
#         # 'LAB',
#         "-filter",
#         "LanczosSharp",
#         '-write',
#         'mpr:copy-of-original',
#         # '+delete',
#         ## Begin generating imgs 
#         # --> Large Jpeg
#         'mpr:copy-of-original',
#         '-format', 
#         'jpg',
#         '-resize',
#         '400x480',
#         # '-gravity',
#         # 'center',
#         # '-background',
#         # 'white',
#         # '-extent', 
#         # '400x480',
#         '-colorspace',
#         'sRGB',
#         '-unsharp',
#         '2x0.5+0.5+0', 
#         '-quality', 
#         '95',
#         '-write',
#         outfile_l,
#         # '+delete',
        
#         ## Medium Jpeg
#         'mpr:copy-of-original',
#         '-format', 
#         'jpg',
#         '-resize',
#         '300x360',
#         # '-gravity',
#         # 'center',
#         # '-background',
#         # 'white',
#         # '-extent', 
#         # '300x360',
#         '-colorspace',
#         'sRGB',
#         '-unsharp',
#         '2x0.5+0.5+0', 
#         '-quality', 
#         '95',
#         '-write',
#         outfile_m,
#         # '+delete',
#         'null:',
#         ])
#     #return
# ##########################################

#####################################################################################################################
# 5 # OLD -- SEE BELOW -- Upload all  _m.jpg @ 400x480 located in the 3_LisPage... folder
#####################################################################################################################
#import os, sys, re, csv, shutil, glob


## Make the success and fail dirs
# archive_uploaded = os.path.join(listpagedir, 'uploaded')
# tmp_failed = os.path.join(listpagedir, 'failed_upload')
# try:
#     os.makedirs(archive_uploaded, 16877)
# except:
#     pass

# try:
#     os.makedirs(tmp_failed, 16877)
# except:
#     pass


# bgremoved_toload = []
# import time, ftplib
# for f in glob.glob(os.path.join(listpagedir, '*_l.??g')):
#     bgremoved_toload.append(os.path.abspath(f))
    
#     try:
#         code = pycurl_upload_imagedrop(f)
#         if code == '200':
#             os.rename(f, f.replace('3_ListPage_to_Load', '4_Archive/JPG/LIST_PAGE_LOADED'))
#             print "Successfully Loaded--> {}".format(f)
#         elif code:
#             print code, f
#             time.sleep(float(.3))
#             try:
#                 ftpload_to_imagedrop(f)
#                 print "Uploaded {}".format(f)
#                 time.sleep(float(.3))
#                 os.rename(f, f.replace('3_ListPage_to_Load', '4_Archive/JPG/LIST_PAGE_LOADED'))
#                 #shutil.move(f, archive_uploaded)
#             except:
#                 #shutil.move(f, tmp_failed)
#                 pass
#     except ftplib.error_temp:
#         print "Failed FTP error", f
#         time.sleep(.2)
#         try:
#             upload_to_imagedrop(f)
#             print "Second Try Got File via FTP", f
#             os.rename(f, f.replace('3_ListPage_to_Load', '4_Archive/JPG/LIST_PAGE_LOADED'))
#         except:
#             try:
#                 os.rename(f, f.replace('3_ListPage_to_Load', 'X_Errors'))
#             except OSError:
#                 print "Final Try Connect error", f
#                 pass
            
#     except EOFError:
#         print "Failed EOF error", f
#         time.sleep(.2)
#         try:
#             upload_to_imagedrop(f)
#             print "Second Try Got File via FTP", f
#             os.rename(f, f.replace('3_ListPage_to_Load', '4_Archive/JPG/LIST_PAGE_LOADED'))
#         except:
#             try:
#                 os.rename(f, f.replace('3_ListPage_to_Load', 'X_Errors'))
#             except OSError:
#                 print "Final Try Connect error", f
#                 pass
    
#     except:
#         print "Failed Connect error", f
#         # os.rename(f, f.replace('3_ListPage_to_Load', 'X_Errors'))
#         time.sleep(1)
#         try:
#             pycurl_upload_imagedrop(f)
#             print "Final Try Got File via FTP", f
#             os.rename(f, f.replace('3_ListPage_to_Load', '4_Archive/JPG/LIST_PAGE_LOADED'))
#             time.sleep(.2)
#         except:
#             try:
#                 os.rename(f, f.replace('3_ListPage_to_Load', 'X_Errors'))
#             except OSError:
#                 print "Final Try Connect error", f
#                 pass

