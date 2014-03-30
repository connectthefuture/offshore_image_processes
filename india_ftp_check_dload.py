import ftplib
import os,sys,re

username   = "bf"
password   = "B1002#@F"
ftpurl     = "prepressoutsourcing.com"
remotepath = 'Pick/'


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

for f in files:
    print f
