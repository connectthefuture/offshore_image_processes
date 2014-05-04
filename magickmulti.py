#!/usr/bin/env python

def subproc_multithumbs_4_2(filepath,destdir):
    import subprocess, os
    
    fname = filepath.split("/")[-1].split('.')[0].lower().replace('_1.','.')
    ext = filepath.split(".")[-1]
 
    outfile_l = os.path.join(destdir, fname + "_l.jpg")    
    outfile_m = os.path.join(destdir, fname + "_m.jpg")

    subprocess.call([
        'convert', 
        filepath, 
        '-format', 
        ext,
#        '-crop',
#        str(
#        subprocess.call(['convert', filepath, '-virtual-pixel', 'edge', '-blur', '0x15', '-fuzz', '1%', '-trim', '-format', '%wx%h%O', 'info:'], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False))
#        ,
#        '-gravity',
#         'center',
#        '-trim',
#        '-colorspace',
#        'LAB',
        "-filter",
        "LanczosSharp",
        '-write',
        'mpr:copy-of-original',
        '+delete',
            ## Begin generating imgs 
            # --> Large Jpeg
            'mpr:copy-of-original',
            '-format', 
            'jpg',
            '-resize',
            '400x480',
            #'-gravity',
            #'center',
#            '-background',
#            'white',
#            '-extent', 
#            '400x480',
            '-colorspace',
            'sRGB',
            '-unsharp',
            '2x0.5+0.5+0', 
            '-quality', 
            '95',
            '-write',
            outfile_l,
            '+delete',
            
            ## Medium Jpeg
            'mpr:copy-of-original',
            '-format', 
            'jpg',
            '-resize',
            '300x360',
            #'-gravity',
            #'center',
#            '-background',
#            'white',
#            '-extent', 
#            '300x360',
            '-colorspace',
            'sRGB',
            '-unsharp',
            '2x0.5+0.5+0', 
            '-quality', 
            '95',
            '-write',
            outfile_m,
            '+delete',
            ])
    #return
            
            
def main(originaldir,destdir=None):
#def multithumbs_batch_doer(originaldir,destdir=None):
    import sys,os, datetime, glob
    todaysdirdate = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d_%f')

    originaldir = os.path.abspath(originaldir)
    os.chdir(originaldir)
    listeddir = os.listdir(originaldir)
    
    if not destdir:
        destdir = os.path.join(originaldir, 'converteddir_' + todaysdirdate)

    if not os.path.isdir(destdir):
        try:
            os.makedirs(destdir)
        except:
            print "Failed {}".format(destdir)
            pass

    print destdir        
    for filepath in listeddir:
        subproc_multithumbs_4_2(os.path.abspath(filepath),destdir)

    allfiles_list = []
    converteddir = glob.glob(os.path.join(destdir, '*[0-9]???????[0-9]_[lmz].jpg'))
    pngs_in_originaldir = glob.glob(os.path.join(originaldir, '*[0-9]???????[0-9].png'))

    for f in converteddir:
        allfiles_list.append(os.path.abspath(f))

    for f in pngs_in_originaldir:
        allfiles_list.append(os.path.abspath(f))


    return allfiles_list


if __name__ == '__main__':
    import sys
    try:
        originaldir = sys.argv[1]
    except IndexError:
        print "You must enter at least the Dir holding the images to process.\vThanks"
    destdir     = ''
    try:
        destdir = sys.argv[2]
    except IndexError:
        pass
else:       
    originaldir = sys.argv[1]
    #destdir     = ''
main(originaldir,destdir)
