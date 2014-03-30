#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
import zipfile,sys,datetime,os,re
regex=re.compile(r'^[^\.].+?[jpng]{3}$')
todaysdate = str(datetime.date.today())
#todaysdate = '2014-01-27'
todaysfolder = "{0}{1}{2}_BC_SET_B".format(todaysdate[5:7],todaysdate[8:10],todaysdate[2:4])
todaysParent = "{0}_{1}".format(todaysdate[5:7],todaysdate[:4])


def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            if re.findall(regex,file):
                filepath = os.path.abspath(file)
                print filepath
                zip.write(os.path.relpath(filepath))#os.path.join(root, file))
                #zip.write(os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

rootdir = sys.argv[1]
filename = "batch_" + todaysdate + ".zip"


dircnt = len(os.listdir(rootdir))


if __name__ == '__main__':
    if dircnt > 501:
        os.chdir(rootdir)
        #zipf = os.path.join(rootdir.replace('1_Sending','2_Returned'), filename)
        zipf = os.path.join(rootdir, filename)
        zipf = zipfile.ZipFile(zipf, 'w')
        zipdir(rootdir, zipf)
        zipf.close()
        