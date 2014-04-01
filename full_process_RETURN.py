#!/usr/bin/env python

#todaysdate = '2014-01-27'
#todaysfolder = "{0}{1}{2}_BC_SET_B".format(todaysdate[5:7],todaysdate[8:10],todaysdate[2:4])
#todaysParent = "{0}_{1}".format(todaysdate[5:7],todaysdate[:4])

#####################################################################################################################
# 1 # FTP Download zip file or files ################################################################################
#####################################################################################################################

def ftp_download_allzips(returndir):
    import ftplib
    import os,sys,re
    #colorstyle = filepath.split('/')[-1][:9]
    #if re.findall(regex_colorstyle, colorstyle):
    username   = "bf"
    password   = "B14300F"
    ftpurl     = "prepressoutsourcing.com"
    remotepath = 'Pick'
    fullftp    = os.path.join(ftpurl, remotepath)
    #returndir = '/mnt/srv/media/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned'
#
    ftp = ftplib.FTP(ftpurl)
    ftp.login(username, password)
    ftp.cwd(remotepath)

    filenames = []
    
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
        ftp.cwd(dname)
        filenames = []
        ftp.retrlines('NLST', filenames.append)

    ##dload
    for filename in filenames:
        local_filename = os.path.join(returndir,filename)
        file = open(local_filename, 'wb')
        ftp.retrbinary('RETR '+ filename, file.write)
        file.close()
    ftp.close()

#####################################################################################################################
# 2 # Unzip downloaded file##########################################################################################
#####################################################################################################################

def unzip_dir_savefiles(zipin, extractdir):
    import zipfile,sys,datetime,os,re
    regex_png = re.compile(r'^[^\.].+?[png]{3}$')
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
                pass
    return zipin

#####################################################################################################################
# 3 and 4 # Magick Crop and save as 400x480 _m.jpg ##################################################################
#####################################################################################################################
def subproc_pad_to_x480(file,destdir):
    import subprocess, os
    
    fname = file.split("/")[-1].split('.')[0].replace('_LP','_m').lower()
    ext = file.split(".")[-1]
    outfile = os.path.join(destdir, fname + ".jpg")    
    
    #try:            
    subprocess.call([
        "convert", 
        file, 
        '-format', 
        'jpg',
        '-crop',
        str(
        subprocess.call(['convert', file, '-virtual-pixel', 'edge', '-blur', '0x15', '-fuzz', '1%', '-trim', '-format', '%wx%h%O', 'info:'], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False))
        ,
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


#####################################################################################################################
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
#####################################################################################################################
# 7 # After Upload set return_dt on offshore_status #################################################################
#####################################################################################################################
def sqlQuery_500_set_returndt(style):
    import sqlalchemy
    mysql_engine_www = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
    connection = mysql_engine_www.connect()
    try:
        connection.execute("""
                UPDATE offshore_status (colorstyle) 
                VALUES (%s) 
                SET return_dt=DATE_FORMAT(NOW(),'%Y-%m-%d');
                """, style)
    except sqlalchemy.exc.IntegrityError:
        print "Duplicate Entry {0}".format(style)
    connection.close()
#####################################################################################################################
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

#####################################################################################################################
# 1 #  Download all zips on remote dir via FTP
#####################################################################################################################

ftp_download_allzips(returndir)

######################################################################################################################
## 2 # After download list zip files dloaded and unzip
#######################################################################################################################
### Grab all downloaded zips in a list prior to extracting pngs
zipfiles_dload = []
for z in glob.glob(os.path.join(returndir, '*.zip')):
    zipfiles_dload.append(os.path.abspath(z))
#
### unzip 
while len(zipfiles_dload) >= 1:
    zipreturned = os.path.abspath(zipfiles_dload.pop())
    parentdir   = '/'.join(zipreturned.split('/')[:-1])
    zipname     = zipreturned.split('/')[-1].split('.')[0]
    extractdir  = os.path.join(parentdir, zipname)
    
    ## Make new dir named as zipfile name without ext to extract zip contents to
    try:
        os.mkdir(extractdir)
    except:# SystemError:
        pass
    
    if os.path.isfile(zipreturned):
        print "ZZZ",zipreturned, extractdir, zipname
        unzip_dir_savefiles(zipreturned, extractdir)
        os.remove(zipreturned)


#####################################################################################################################
# 3 # After unzip of complete PNGs Archive and Create new List page image
#####################################################################################################################
## Get all extracted PNGs and rename with _LP ext and move to archive dir 4, then copy/create _m.jpg in 3_ListPage_to_Load
extracted_pngs = []
for f in glob.glob(os.path.join(returndir, '*/*.png')):
    extracted_pngs.append(os.path.abspath(f))

while len(extracted_pngs) >= 1:
    extractedpng       = os.path.abspath(extracted_pngs.pop())
    parentdir          = '/'.join(extractedpng.split('/')[:-1])
    filename           = extractedpng.split('/')[-1]
    colorstyle         = extractedpng.split('/')[-1].split('.')[0]
    pngarchived_pardir = '/'.join(extractedpng.split('/')[:-1]).replace('2_Returned','4_Archive')
    pngarchived_fname  = extractedpng.split('/')[-1].replace('.png', '_LP.png')
    pngarchived_path   = os.path.join(pngarchived_pardir, pngarchived_fname)
    
    try:
        os.makedirs(pngarchived_pardir)
    except:
        print "Failed makedirs"

    if os.path.isfile(pngarchived_path):
        pass
    else:
        shutil.move(extractedpng, pngarchived_path)
        subproc_pad_to_x480(pngarchived_path,listpagedir)

## Remove empty dir after padding etc
if len(os.listdir(parentdir)) == 0: os.rmdir(parentdir)

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

        
#####################################################################################################################
# 5 # Upload all  _m.jpg @ 400x480 located in the 3_LisPage... folder
#####################################################################################################################
listpage_jpgs_toload = []
for f in glob.glob(os.path.join(listpagedir, '*_m.jpg')):
    listpage_jpgs_toload.append(os.path.abspath(f))
    try:
        upload_to_imagedrop(f)
        os.rename(f, f.replace('3_ListPage_to_Load', '4_Archive/JPG/LIST_PAGE_LOADED'))
    except ftplib.error_temp:
        print "Failed FTP error", f
        os.rename(f, f.replace('3_ListPage_to_Load', 'X_Errors'))
    except EOFError:
        print "Failed EOF error", f
        os.rename(f, f.replace('3_ListPage_to_Load', 'X_Errors'))

#####################################################################################################################
# 6 # After Uploading from 3_ dir, Archive all the _LP files in dated dir under archive/PNG/etc.....
#####################################################################################################################
## Gather all _LP files and store in dated dir under 4_Archive/PNG/<todays date>
archive_ready = []
for f in glob.glob(os.path.join(archdir, '*/*_LP.png')):
    archive_ready.append(os.path.abspath(f))
    archivedir = os.path.join(archdir, 'PNG', todaysdate + '_uploaded')
    colorstyle = f.split('/')[-1][:9]
    try:
        os.makedirs(archivedir)
    except:
        print "Failed makedirs for Archiving"
    try:
        shutil.move(f, archivedir)
    except shutil.Error:
        os.rename(f, os.path.join(archivedir, f.split('/')[-1]))

    #####################################################
    # 7 # Update offshore_status with todays date as sent
    #####################################################
    try:
        sqlQuery_500_set_returndt(colorstyle)
    except:
        print "Failed Entrering Return dt for --> {0}".format(colorstyle)
    #####################################################
    #####################################################