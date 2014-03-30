#!/usr/bin/env python
import zipfile,sys,datetime,os,re
regex_zipfilename=re.compile(r'^[^\.].+?[zipZIP]{3}$')
regex_zipfilepath=re.compile(r'^/.+?[zipZIP]{3}$')

todaysdate = str(datetime.date.today())
#todaysdate = '2014-01-27'
todaysfolder = "{0}{1}{2}_BC_SET_B".format(todaysdate[5:7],todaysdate[8:10],todaysdate[2:4])
todaysParent = "{0}_{1}".format(todaysdate[5:7],todaysdate[:4])

zipin  = os.path.abspath(sys.argv[1])
zipdir = zipin.split('/')[:-1]
# Open zip file
zipf   = zipfile.ZipFile(zipin, 'r')

# ZipFile.read returns the bytes contained in named file
filenames = zipf.namelist()

for filename in filenames:
    print 'Processing {0}'.format(filename)
    f = zipf.open(filename)
    contents = f.read()
    print os.path.abspath(filename)
    with open(filename, 'wb') as wfile:
        wfile.write(contents)

#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
