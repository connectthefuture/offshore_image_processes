#!/usr/bin/env python

###
## Walk Root Directory and Return List or all Files in all Subdirs too
def recursive_dirlist(rootdir):
    import os
    walkedlist = []
    for dirname, subdirnames, filenames in os.walk(rootdir):
        # append path of all filenames to walkedlist
        for filename in filenames:
            file_path = os.path.abspath(os.path.join(dirname, filename))
            if os.path.isfile(file_path):
                walkedlist.append(file_path)
    # Advanced usage:
    # editing the 'dirnames' list will stop os.walk() from recursing into there.
    #if '.git' in dirnames:
    # don't go into any .git directories.
    #    dirnames.remove('.git')
    return walkedlist


###
## Extract All Metadata from Image File as Dict
def get_exif(file_path):
    from PIL import Image
    from PIL.ExifTags import TAGS
    exifdata = {}
    im = Image.open(file_path)
    info = im._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        exifdata[decoded] = value
    return exifdata

###
## Write Rows to Dated CSV in Users Home Dir If Desired
def csv_write_datedOutfile(lines):
    import csv,datetime,os
    dt = str(datetime.datetime.now())
    today = dt.split(' ')[0]
    f = os.path.join(os.path.expanduser('~'), today + '_datastrings.csv')
    for line in lines:
        with open(f, 'ab+') as csvwritefile:
            writer = csv.writer(csvwritefile, delimiter='\n')
            writer.writerows(lines)

############################ Run ######################################################## Run ############################
############################ Run ######################################################## Run ############################

from PIL import Image
import os,sys,re,shutil

rootdir = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval' 
#sys.argv[1]
walkedout = recursive_dirlist(rootdir)

regex = re.compile(r'^/.+?\.[a-zA-Z2]{3}$')
regex_india_ready = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/1_Sending/.*?/?[0-9]{9}\.[pngPNG]{3}$')
regex_india_prezipdir = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/1_Sending/batch_[0-9]{6}/.*?\.[pngPNG]{3}$')
regex_india_prezip = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/1_Sending/batch_[0-9]{6}\.[zipZIP]{3}$')

regex_india_postzip = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned/batch_[0-9]{6}\.[zipZIP]{3}$')
regex_india_postzipdir = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned/batch_[0-9]{6}/.*?\.[pngPNG]{3}$')

regex_m_uploading = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/3_ListPage_to_Load/[0-9]{9}_m\.[jpgJPG]{3}$')

regex_arch_m_uploaded = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/JPG/LIST_PAGE_LOADED/[0-9]{9}_[LlMm]\.[jpgJPG]{3}$')
regex_arch_postzip = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/ZIP/batch_[0-9_-]{6,22}\.[zipZIP]{3}$')
regex_arch_newpng = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/PNG/?.*?/[0-9]{9}_LP\.[pngPNG]{3}$')
regex_arch_origpng = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/PNG_SENT/?.*?/[0-9]{9}\.[pngPNG]{3}$')

regex_india_postzipdir = re.compile(r'^/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/.*?/?batch_[0-9]{6}/[0-9]{9}_?L?P?.[pngPNG]{3}$')
#regex = re.compile(r'.+?/.[jpgJPG]{3}$')
offshore_senddir1     = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/1_Sending'
offshore_returndir2   = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/2_Returned'
offshore_margejpgdir3 = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/3_ListPage_to_Load'
offshore_archdir4     = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive'

datastrings = []
datastringsdict = {}
for line in walkedout:
    datastringsdict_tmp = {}
    if re.findall(regex,line):
        try:
            file_path      = line
            filename       = file_path.split('/')[-1]
            directorypath  = os.path.dirname(file_path)
            zip_groupdir   = directorypath.split('/')[-2]
            colorstyle     = filename[:9]
            ext            = filename.split('.')[-1]
            archivedir     = ext.upper()
            archivehash4   = filename[:4]

            file_path_pre      = os.path.join(offshore_senddir1, filename)
            file_path_post     = os.path.join(offshore_returndir2, zip_groupdir, filename)
            file_path_zip      = os.path.join(offshore_senddir1, zip_groupdir)
            file_path_prezip   = os.path.join(offshore_senddir1, zip_groupdir + ext)
            file_path_postzip  = os.path.join(offshore_archdir4, archivedir, zip_groupdir + ext)
            file_path_archpng  = os.path.join(offshore_archdir4, "PNG", colorstyle + "_LP.png")
            file_path_archorigpng  = os.path.join(offshore_archdir4, "PNG_SENT", colorstyle + ".png")
#            try:
#                photo_date = get_exif(file_path)['DateTimeOriginal'][:10]
#            except KeyError:
#                try:
#                    photo_date = get_exif(file_path)['DateTime'][:10]
#                except KeyError:
#                    photo_date = 0000-00-00
#            photo_date = photo_date.replace(':','-')

            datastringsdict_tmp['file_path_pre'] = file_path_pre
            datastringsdict_tmp['file_path_post'] = file_path_post
            datastringsdict_tmp['file_path_zip'] = file_path_zip
            datastringsdict_tmp['file_path_prezip'] = file_path_prezip
            datastringsdict_tmp['file_path_postzip'] = file_path_postzip
            datastringsdict_tmp['file_path_archpng'] = file_path_archpng
            datastringsdict_tmp['file_path_archorigpng'] = file_path_archorigpng
            datastringsdict_tmp['colorstyle'] = colorstyle
            datastringsdict_tmp['archivedir'] = archivedir
            datastringsdict_tmp['zip_groupdir'] = zip_groupdir
            datastringsdict_tmp['directorypath'] = directorypath
            datastringsdict[file_path] = datastringsdict_tmp
#file_path_reletive = file_path.replace('/mnt/Post_Ready/zImages_1/', '/zImages/')
            file_path_reletive = file_path.replace('JPG', 'jpg')
# Format CSV Rows
            row = "{0},{1},{2},{3},{4}".format(colorstyle,zip_groupdir,file_path_pre,file_path_post,file_path_zip)
            #print row
            datastrings.append(row)
        except IOError:
            print "IOError on {0}".format(line)
        except AttributeError:
            print "AttributeError on {0}".format(line)

## Write CSV List to dated file for Import to MySQL
#csv_write_datedOutfile(datastrings)
import datetime
todaysdate = datetime.date.today()
#Iterate through Dict of Walked Directory, then Import to MySql DB
import sqlalchemy
## First compile the SQL Fields as key value pairs
fulldict = {}
for k,v in datastringsdict.iteritems():
    dfill = {}
    dfill['colorstyle'] = v['colorstyle']
    #dfill['photo_date'] = v['photo_date']
    file_path = k
    dfill['file_path_pre'] = v['file_path_pre']
    dfill['file_path_post'] = v['file_path_post']
    dfill['file_path_zip'] = v['file_path_zip']
    dfill['file_path_prezip'] = v['file_path_prezip']
    dfill['file_path_postzip'] = v['file_path_postzip']
    dfill['file_path_archpng'] = v['file_path_archpng']
    dfill['file_path_archorigpng'] = v['file_path_archorigpng']

    fulldict[k] = dfill

print fulldict.items()
## Take the compiled k/v pairs and Format + Insert into MySQL DB
for k,v in fulldict.iteritems():
    try:

        mysql_engine = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@localhost:3301/www_django')
#        mysql_engine = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
        connection = mysql_engine.connect()
        ## /mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/1_Sending
        ## Test File path String to Determine which Table needs to be Updated Then Insert SQL statement
        sqlinsert_choose_test = k


## zip returned and ready to convert to _m and load
        if re.findall(regex_arch_m_uploaded, sqlinsert_choose_test):
            #print "POSTZIP"
        #if os.path.isfile(v['file_path_postzip']):
#            connection.execute("""INSERT INTO offshore_zip (colorstyle, file_path_post, file_path_zip) VALUES (%s, %s, %s)
#            ON DUPLICATE KEY UPDATE 
#                        file_path_post       = VALUES(file_path_post), 
#                        file_path_zip        = VALUES(file_path_zip); 
#                        """, v['colorstyle'], k,  v['file_path_post'])
#            print "Successful Insert offshore_Zip --> {0}".format(k)
            connection.execute("""INSERT INTO offshore_status (colorstyle, file_path_post, return_dt) VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                            file_path_post = VALUES(file_path_post), 
                            return_dt      = VALUES(return_dt); 
                            """, v['colorstyle'], k, todaysdate)
            print "Successful Insert to offshore_Status --> {0}".format(k)
        #else:
        #     print "File Doesnt Exist --> {0}".format(v['file_path_postzip'])

### Png ready to be packed and sent once quota reached
        elif re.findall(regex_arch_origpng, sqlinsert_choose_test):
            
            #if os.path.isfile(v['file_path_pre']):
            connection.execute("""INSERT INTO offshore_status (colorstyle, file_path_pre, send_dt) VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                            file_path_pre        = VALUES(file_path_pre),
                            send_dt              = VALUES(send_dt); 
                            """, v['colorstyle'], k, todaysdate)  #v['file_path_pre'])
            print "Successful Insert to offshore_Status --> {0}".format(k)
#            connection.execute("""INSERT INTO offshore_zip (colorstyle, file_path_pre) VALUES (%s, %s)
#            ON DUPLICATE KEY UPDATE 
#                            file_path_pre        = VALUES(file_path_pre), 
#                            """, v['colorstyle'], k)  ##v['file_path_pre'])
#            print "Successful Insert to offshore_Status --> {0}".format(k)
            #else:
            #    print "Error entering --> {0}\t File doesnt seem to Exist".format(v['file_path_pre'])

        elif re.findall(regex_arch_postzip, sqlinsert_choose_test):
            if os.path.isfile(v['file_path_postzip']):
                connection.execute("""INSERT INTO offshore_zip (colorstyle, file_path_pre, file_path_post, file_path_zip) VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                            file_path_pre         = VALUES(file_path_pre),
                            file_path_post        = VALUES(file_path_post),  
                            file_path_zip         = VALUES(file_path_zip); 
                            """, v['colorstyle'],   v['file_path_archorigpng'], v['file_path_archpng'], k)
                print "Successful Insert offshore_Zip --> {0}".format(k)

        
        else:
            print "Database Table not Found for Inserting {0}".format(k)

    except sqlalchemy.exc.IntegrityError:
        print "Duplicate Entry {0}".format(k)
        