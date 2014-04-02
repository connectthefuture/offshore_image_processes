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