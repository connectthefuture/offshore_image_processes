import ftplib
import os,sys,re

files = []
ftp = ftplib.FTP("prepressoutsourcing.com")
ftp.login("bf", "B1002#@F")
remotepath=('Drop/')

try:
    files = ftp.nlst(remotepath)
except ftplib.error_perm, resp:
    if str(resp) == "550 No files found":
        print "No files in this directory"
    else:
        raise

for f in files:
    batchdir = f.split('/')[-1][:12]
    print batchdir
    if sql_testOffshoreSend(batchdir):        
        print os.path.abspath(f).split('/')[-1]
