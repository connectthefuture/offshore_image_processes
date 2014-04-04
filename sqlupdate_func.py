#!/usr/bin/python

import MySQLdb

# Open database connection
db = MySQLdb.connect("localhost","testuser","test123","TESTDB" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# Prepare SQL query to UPDATE required records
sql = "UPDATE EMPLOYEE SET AGE = AGE + 1
                          WHERE SEX = '%c'" % ('M')
try:
   # Execute the SQL command
   cursor.execute(sql)
   # Commit your changes in the database
   db.commit()
except:
   # Rollback in case there is any error
   db.rollback()

# disconnect from server
db.close()

listpg='/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/JPG/LIST_PAGE_LOADED/330904601_m.jpg'
pngorigsent='/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/PNG_SENT/327964701.png'
pngreturn='/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/PNG/2014-04-01_uploaded/328384001_LP.png'






###
## 4 Last Step is updating the db with what was sent
### Update send dt based on 1000 limit query to send
def sqlQuery_1000_set_senddt(colorstyles_list):
    import sqlalchemy
    mysql_engine_www = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
    connection = mysql_engine_www.connect()
    for style in colorstyles_list:
        try:
#            connection.execute("""
#                    UPDATE offshore_status (colorstyle) VALUES (%s)
#                    SET send_dt=DATE_FORMAT(NOW(),'%Y-%m-%d');
#                    """, style)
#
            connection.execute("""
                    INSERT INTO offshore_status (colorstyle)
                    VALUES (%s)
                    ON DUPLICATE KEY UPDATE
                    send_dt    = VALUES (CURDATE())
                    """, style)
        except sqlalchemy.exc.IntegrityError:
            print "Duplicate Entry {0}".format(k)
    connection.close()


############
def sqlQuery_1000_set_offshorezip_sent(colorstyles_list, zipbatch):
    import sqlalchemy
    arch_png_sent = '/mnt/Post_Complete/Complete_Archive/SendReceive_BGRemoval/4_Archive/PNG_SENT'
    mysql_engine_www = sqlalchemy.create_engine('mysql+mysqldb://root:mysql@prodimages.ny.bluefly.com:3301/www_django')
    connection = mysql_engine_www.connect()
    for style in colorstyles_list:
        file_path_pre = os.path.join(arch_png_sent, style, '.png')
        try:
            connection.execute("""
                    INSERT INTO offshore_zip (colorstyle, file_path_pre, zipbatch)
                    VALUES (%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                    file_path_pre    = VALUES (file_path_pre)
                    zipbatch         = VALUES (zipbatch)
                    """, style, file_path_pre, zipbatch)
        except sqlalchemy.exc.IntegrityError:
            print "Duplicate Entry {0}".format(k)
    connection.close()
## 4a update zip table with style, path to sent png, and name of zip file as zipbatch id
zipbatch = zipname.split('/')[-1].split('.')[0]
sqlQuery_1000_set_offshorezip(styles_to_send,zipbatch)



#### sending file
## Write Rows to Dated CSV in Users Home Dir If Desired
def csv_write_datedCacheClearList(lines, destdir=None):
    import csv,datetime,os
    dt = str(datetime.datetime.now())
    today = dt.split(' ')[0]
    if not destdir:
        destdir = os.path.expanduser('~')
    f = os.path.join(destdir, today + '_clearedgecast.csv')
    with open(f, 'ab+') as csvwritefile:
        writer = csv.writer(csvwritefile, delimiter='\n', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        for line in lines:
            writer.writerow([line])


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
