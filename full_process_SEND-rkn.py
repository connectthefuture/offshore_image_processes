#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zipfile,sys,datetime,os,re,glob


todaysdate = str(datetime.date.today())

#####################################################
# 2 # Upload to RKN etc. FTP
#####################################################################################################################
def upload_to_rkn(file):
    import ftplib, datetime, os
    todaysdate_senddt = "{0:%B%d}".format(datetime.date.today())
    username   = "_partner_3423"
    password   = "Sell3423"
    ftpurl     = "upload.rakuten.ne.jp"
    remotepath = str('Bluefly Images/images' + todaysdate_senddt)
    fullftp    = os.path.join(ftpurl, remotepath)
    failed     = ''
    session = ftplib.FTP(ftpurl, username, password)
    try:
        
        fileread = open(file, 'rb')
        filename = str(file.split('/')[-1])
        try:
            session.mkd(remotepath)
        except:
            pass
        session.cwd(remotepath)
        
        try:
            session.storbinary('STOR ' + filename, fileread, 8*1024)
        except:
            pass
        
        fileread.close()
        return None
    except:
        failed = os.path.abspath(file)
        return failed
    
    #session.quit()


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
## Query db for 1500 not sent files return colorstyles
def sqlQuery_1500_imgready_notsent():
    import sqlalchemy, sys
    mysql_engine_www = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
    connection = mysql_engine_www.connect()
    try:
        qtysending = sys.argv[1]
        if not qtysending.isdigit():
            qtysending = 1500
    except IndexError:
        qtysending = 1500
    querymake_1500notsent = "SELECT colorstyle FROM offshore_status WHERE product_type not like 'sunglasses' AND image_ready_dt IS NOT NULL AND (send_dt IS NULL AND return_dt IS NULL) ORDER BY available_ct DESC, image_ready_dt DESC LIMIT 0,{0}".format(str(qtysending))

    result = connection.execute(querymake_1500notsent)
    colorstyles_list = []
    for row in result:
        colorstyles_list.append(row['colorstyle'])
    connection.close()

    return set(sorted(colorstyles_list))

###
## 4 Last Step is updating the db with what was sent
### Update send dt based on 1500 limit query to send
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
#rootdir = ''
#try:
csvfile = sys.argv[1]
rootdir = sys.argv[2]
styles_to_send = []
if os.path.isfile(csvfile):
    with open(csvfile, 'rbU') as f:
        s = f.read()
        styles_to_send.append(s.split('\n'))
        
#except IndexError:
#    rootdir = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/1_Sending'

## clear send folder
if not os.path.isdir(rootdir):
    os.makedirs(rootdir)
else:    
    sendglob = glob.glob(os.path.join(rootdir, '*.??g'))
    for g in sendglob:
        os.remove(g)
###### Cleared #####


#if not styles_to_send:
    #styles_to_send = sqlQuery_1500_imgready_notsent()
import time
count = len(styles_to_send[0])
for style in styles_to_send[0]:
    print '{} Files Remaining to Download'.format(count)
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
    count -= 1
##
### After sending zip use the styles_to_send variable list and update the send_dt
##
#####################################################################################################################
#####################################################################################################################
# 1 #
## Check Root dir sys.argv[1], for 1500 files then create a zip called batch_<todays date yyyy-mm-dd>
import glob
regex = re.compile(r'^[^\.].+?[^Zz]..$')
regex_colorstyle = re.compile(r'^[0-9]{9}$')

## unique datetime with microseconds for unique folder names
todaysdirdate = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d_%f')

filename = "batch_" + todaysdirdate + ".zip"
filelist = []

filelist = glob.glob(os.path.join(os.path.abspath(os.curdir), '*.png'))
#  2  ########## Send Zipped files with ftp --> previous Args remain active and used ###################################


failed = []
count = len(filelist)
for f in filelist:
    print '{} Files Remaining to Send'.format(count)
    if_failed = upload_to_rkn(f)
    if if_failed:
        styles_to_send.remove(if_failed)
        failed.append(if_failed)
    
    count -= 1


##TODO:upload ziptosend to  remote zip via ftp then send inserts colorstyles_sent_dt_key to offshore_to_send and offshore_zip
# 4 # Update offshore_status with todays date as sent
if failed:
    print 'FAILED LOAD TO RKN -->{}'.format(failed)
else:
    print 'Totally Loaded -- No Errors'
#sqlQuery_set_senddt(styles_to_send)
