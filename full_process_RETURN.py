#!/usr/bin/env python
import zipfile,sys,datetime,os,re

#todaysdate = '2014-01-27'
#todaysfolder = "{0}{1}{2}_BC_SET_B".format(todaysdate[5:7],todaysdate[8:10],todaysdate[2:4])
#todaysParent = "{0}_{1}".format(todaysdate[5:7],todaysdate[:4])


#####################################################################################################################

def unzip_dir_savefiles(zipin):
    zipin  = os.path.abspath(zipin)
    zipdir = '/'.join(zipin.split('/')[:-1])
    # print zipdir
    # Open zip file
    zipf   = zipfile.ZipFile(zipin, 'r')
    # ZipFile.read returns the bytes contained in named file
    filenames = zipf.namelist()
    for filename in filenames:
        print 'Processing {0}'.format(filename)
        f = zipf.open(filename)
        contents = f.read()
        writefile = os.path.join(zipdir,filename)
        with open(writefile, 'w') as wfile:
            wfile.write(contents)
    return zipin


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
##### FTP download Zip file##########################################################################################
#####################################################################################################################

import ftplib
import os,sys,re


username   = "bf"
password   = "B1002#@F"
ftpurl     = "prepressoutsourcing.com"
remotepath = 'Pick'
fullftp    = os.path.join(ftpurl, remotepath)

files = []
ftp = ftplib.FTP(ftpurl)
ftp.login(username, password)


try:
    files = ftp.nlst(remotepath)
except ftplib.error_perm, resp:
    if str(resp) == "550 No files found":
        print "No files in this directory"
    else:
        raise


for file in files:
    parentdir   = file.split('/')[-1]
    downloaddir = os.path.join(fullftp, parentdir)
    ##TODO: download remote zip via ftp then unzip_dir_savefiles(zipin)
    print downloaddir

#####################################################################################################################
##### Unzip downloaded file##########################################################################################
#####################################################################################################################

regex_zipfilename = re.compile(r'^[^\.].+?[zipZIP]{3}$')
regex_zipfilepath = re.compile(r'^/.+?[zipZIP]{3}$')

todaysdate = str(datetime.date.today())


#colorstyle = filepath.split('/')[-1][:9]
#if re.findall(regex_colorstyle, colorstyle):
ftp = ftplib.FTP(ftpurl)
ftp.login(username, password)
ftp.cwd(remotepath)


filenames = []
ftp.retrlines('NLST', filenames.append)

print filenames

## if filenames is a dir decend into dirand list again till there are files found then dload
if len(filenames) == 1:
    ftp.cwd(filenames.pop())
    filenames = []
    ftp.retrlines('NLST', filenames.append)

print filenames

#rootdir = sys.argv[1]
#returndir = '/mnt/srv/media/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned'
returndir = '/Users/JCut/Dropbox/DEVROOT/srv/media/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned'

for filename in filenames:
    local_filename = os.path.join(returndir,filename)
    file = open(local_filename, 'wb')
    ftp.retrbinary('RETR '+ filename, file.write)

    file.close()

ftp.close()


######### find out how many zips dloaded then extract pngs from zip
zipfiles_returned = []
for z in os.listdir(returndir):
    if re.findall(regex_zipfilepath, z):
        zipfiles_returned.append(z)

if len(zipfiles_returned) == 1:
    zipreturned = zipfiles_returned.pop()
    unzip_dir_savefiles(zipreturned)
else:
    for z in zipreturned:
        unzip_dir_savefiles(z)

