#!/usr/bin/env python
import zipfile,sys,datetime,os,re

todaysdate = str(datetime.date.today())
#todaysdate = '2014-01-27'
todaysfolder = "{0}{1}{2}_BC_SET_B".format(todaysdate[5:7],todaysdate[8:10],todaysdate[2:4])
todaysParent = "{0}_{1}".format(todaysdate[5:7],todaysdate[:4])


def zipdir(path, zip):
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
def upload_to_imagedrop(file):
    import ftplib
    username   = "bf"
    password   = "B1002#@F"
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
################### 1) Crate Zip if 500+ pngs to send  ##############################################################
################### 2) Send Zipped files with ftp   #################################################################
################### 3) Archive zip  #################################################################################
################### 4)    ###########################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
# 1 #
## Check Root dir sys.argv[1], for 500 files then create a zip called batch_<todays date yyyy-mm-dd>
regex            = re.compile(r'^[^\.].+?[^Zz]..$')
regex_colorstyle = re.compile(r'^[0-9]{9}$')


rootdir = sys.argv[1]

filename = "batch_" + todaysdate + ".zip"
dircnt   = len(os.listdir(rootdir))
zipname  = os.path.join(rootdir, filename)


if dircnt > 250:
    os.chdir(rootdir)
    zipf = zipfile.ZipFile(zipname, 'w')
    zlist, zdict = zipdir(rootdir, zipf)
    zipf.close()


#  2  ########## Send Zipped files with ftp --> previous Args remain active and used ###################################
import ftplib
import os,sys,re


username   = "bf"
password   = "B1002#@F"
ftpurl     = "prepressoutsourcing.com"
remotepath = 'Drop'
fullftp    = os.path.join(ftpurl, remotepath)

if dircnt > 250:
    files = []
    ftp = ftplib.FTP(ftpurl)
    ftp.login(username, password)

    ziptosend               = zipname
    colorstyles_sent        = zlist
    colorstyles_sent_dt_key = zdict

    print ziptosend
    print colorstyles_sent_dt_key

    # 2 # Upload to india
    upload_to_imagedrop(ziptosend)
    # 3 # Move Zip to archive after sent
    os.rename(ziptosend, ziptosend.replace('1_Sending','4_Archive/ZIP'))

##TODO:upload ziptosend to  remote zip via ftp then send inserts colorstyles_sent_dt_key to offshore_to_send and offshore_zip

