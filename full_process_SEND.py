#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zipfile,sys,datetime,os,re

todaysdate = str(datetime.date.today())
#todaysdate = '2014-01-27'

def zipdir(path, zip):
    import re,zipfile,os
    sentdate_dict = {}
    zipstyleslist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if re.findall(regex,file):
                filepath   = os.path.abspath(file)
                colorstyle = filepath.split('/')[-1][:9]
                rootdir    = filepath.split('/')[-2]
                if re.findall(regex_colorstyle, colorstyle):
                    zipstyleslist.append(colorstyle)
                    zip.write(os.path.relpath(filepath))
                    os.rename(filepath, filepath.replace('1_Sending/', '4_Archive/PNG_SENT/'))
    sentdate_dict[todaysdate] = zipstyleslist
    return zipstyleslist, sentdate_dict

#####################################################
# 2 # Upload to prepress etc. FTP
#####################################################################################################################
def upload_to_india(file):
    import ftplib
    username   = "bf"
    password   = "B14300F"
    ftpurl     = "prepressoutsourcing.com"
    remotepath = 'Drop/'
    fullftp    = os.path.join(ftpurl, remotepath)

    session = ftplib.FTP(ftpurl, username, password)
    fileread = open(file, 'rb')
    filename = str(file.split('/')[-1])
    session.cwd(remotepath)
    session.storbinary('STOR ' + filename, fileread, 8*1024)
    fileread.close()
    session.quit() 
#############################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
################### 1) Crate Zip if 1000+ pngs to send  ##############################################################
################### 2) Send Zipped files with ftp   #################################################################
################### 3) Archive zip  #################################################################################
################### 0) Query db get 1000 to send from netsrv101    ###################################################
#####################################################################################################################
### 0 ###
## Path to file below is from the mountpoint on FTP, ie /mnt/images..
## Download via FTP
def getbinary_ftp_netsrv101(remote_pathtofile, outfile=None):
    # fetch a binary file
    import ftplib
    session = ftplib.FTP("netsrv101.l3.bluefly.com", "imagedrop", "imagedrop0")
    if outfile is None:
        outfile = sys.stdout
    destfile = open(outfile, "wb")
    print remote_pathtofile
    session.retrbinary("RETR " + remote_pathtofile, destfile.write, 8*1024)
    destfile.close()
    session.quit()

###
## Query db for 1000 not sent files return colorstyles 
def sqlQuery_1000_imgready_notsent():
    import sqlalchemy
    mysql_engine_www = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
    connection = mysql_engine_www.connect()
    
    querymake_1000notsent = """SELECT colorstyle FROM offshore_status WHERE image_ready_dt IS NOT NULL AND (send_dt IS NULL AND return_dt IS NULL) ORDER BY image_ready_dt DESC LIMIT 0,400;"""
    
    result = connection.execute(querymake_1000notsent)
    colorstyles_list = []
    for row in result:
        colorstyles_list.append(row['colorstyle'])
    connection.close()
    
    return set(sorted(colorstyles_list))

###
## 4 Last Step is updating the db with what was sent
### Update send dt based on 1000 limit query to send    
def sqlQuery_set_senddt(colorstyles_list):
    import sqlalchemy, datetime
    todaysdate_senddt = str(datetime.date.today())
    mysql_engine_www = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
    connection = mysql_engine_www.connect()
    for style in colorstyles_list:
        try:
            sql = "UPDATE offshore_status SET send_dt='{0}' WHERE colorstyle='{1}'".format(todaysdate_senddt, style)
            connection.execute(sql)
        except sqlalchemy.exc.IntegrityError:
            print "Duplicate Entry {0}".format(style)
    connection.close()
#####################################################################################################################
# RUN 0 Process #####################################################################################################
#####################################################################################################################
rootdir = ''
try:
    rootdir = sys.argv[1]
except:
    rootdir = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/1_Sending'

styles_to_send = sqlQuery_1000_imgready_notsent()
import time, ftplib
for style in styles_to_send:
    colorstyle = style
    hashdir = colorstyle[:4]
    colorstyle_file = colorstyle + ".png"
    remotedir = "/mnt/images/images"
    remotepath = os.path.join(remotedir, hashdir, colorstyle_file)
    destpath = os.path.join(rootdir, colorstyle_file)

    try:
        getbinary_ftp_netsrv101(remotepath, outfile=destpath)
        print "Got File via FTP", colorstyle
    except ftplib.error_temp:
        print "Failed FTP Lib error", colorstyle
        #time.sleep(.5)
        try:
            getbinary_ftp_netsrv101(remotepath, outfile=destpath)
            print "Second Try Got File via FTP", colorstyle
        except:
            pass
    except EOFError:
        print "Failed EOF error", colorstyle
        time.sleep(1)
        try:
            getbinary_ftp_netsrv101(remotepath, outfile=destpath)
            print "Second Try Got File via FTP", colorstyle
        except:
            pass
    except:
        print "Failed Connect error", colorstyle
        time.sleep(1)
        try:
            getbinary_ftp_netsrv101(remotepath, outfile=destpath)
            print "Second Try Got File via FTP", colorstyle
        except:
            pass

##   
### After sending zip use the styles_to_send variable list and update the send_dt
##
#####################################################################################################################
#####################################################################################################################
# 1 #
## Check Root dir sys.argv[1], for 1000 files then create a zip called batch_<todays date yyyy-mm-dd>
regex            = re.compile(r'^[^\.].+?[^Zz]..$')
regex_colorstyle = re.compile(r'^[0-9]{9}$')

## unique datetime with microseconds for unique folder names
todaysdirdate = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d_%f')

filename = "batch_" + todaysdirdate + ".zip"
dircnt   = len(os.listdir(rootdir))
zipname  = os.path.join(rootdir, filename)

zipfilelist = []
zipfilelist.append(zipname)
zipcount = 1
while len(os.listdir(rootdir)) >= 1:
    os.chdir(rootdir)
    zipf = zipfile.ZipFile(zipname, 'w') ####allowZip64=True)
    try:
        zlist, zdict = zipdir(rootdir, zipf)
    except zipfile.LargeZipFile:
        zipf.close()
        if len(os.listdir(rootdir)) >= 1:
            zipcount = + 1
            zipname = os.path.join(rootdir, filename).replace('.zip', "_{0}.zip".format(zipcount))
            zipfilelist.append(zipname)
## Close Last zipfile
zipf.close()

##
#  2  ########## Send Zipped files with ftp --> previous Args remain active and used ###################################
import ftplib
import os,sys,re


username   = "bf"
password   = "B14300F"
ftpurl     = "prepressoutsourcing.com"
remotepath = 'Drop'
fullftp    = os.path.join(ftpurl, remotepath)

if dircnt >= 1:
    while len(zipfilelist) >= 1:

        files = []
        ftp = ftplib.FTP(ftpurl)
        ftp.login(username, password)

        ziptosend                           = zipfilelist.pop()
        colorstyles_sent                = zlist
        colorstyles_sent_dt_key  = zdict

        # 2 # Upload to india
        upload_to_india(ziptosend)
        # 3 # Move Zip to archive after sent
        os.rename(ziptosend, ziptosend.replace('1_Sending','4_Archive/ZIP_SENT'))

##TODO:upload ziptosend to  remote zip via ftp then send inserts colorstyles_sent_dt_key to offshore_to_send and offshore_zip
# 4 # Update offshore_status with todays date as sent
sqlQuery_set_senddt(styles_to_send)
