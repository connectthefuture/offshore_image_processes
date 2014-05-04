import ftplib
import os,sys,re

import ftplib
import os,sys,re

files = []
username   = "bf"
password   = "B14300F"
ftpurl     = "prepressoutsourcing.com"
remotepath = os.path.join('Pick',sys.argv[1])
fullftp    = os.path.join(ftpurl, remotepath)
#returndir = '/mnt/srv/media/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned'
#

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

destdir='~/Public'
for f in files:
    print f.split('/')[-1].strip('.png')
    ftp.retrbinary(f,destdir)