# -*- coding: utf-8 -*-

import os, subprocess, sys, sqlite3, hashlib

# Also works with softlinks, e.g. ln -s /home/user/Pictures images
IMAGE_FOLDER     = u"images".encode("utf-8")
THUMBNAIL_FOLDER = u"thumbs".encode("utf-8")
EXCLUDE_FOLDERS  = ["example_dir"]


conn = sqlite3.connect('imagetag.sqlite')
c = conn.cursor()

c.execute("""SELECT filepath FROM files""")
dbFiles = c.fetchall()

def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def makeThumb(filepath):
    thumbpath = md5(filepath) + ".jpg"
    while os.path.isfile(os.path.join(
            THUMBNAIL_FOLDER,
            os.path.split(thumbpath)[1])):
        name, ext = os.path.splitext(thumbpath)
        thumbpath = name + "_" + ext
    
    cmd = """
    convert "{0}"[0] -thumbnail 100x100^ -gravity center -crop \
    100x100+0+0  +repage "{1}"
    """.format(filepath, os.path.join(THUMBNAIL_FOLDER, thumbpath))
    os.system(cmd)
    return thumbpath

def getSize(path):
    dim = subprocess.Popen(["identify","-format","%w,%h;", path], 
                           stdout=subprocess.PIPE).communicate()[0]
    dim = dim.split(";")[0] # identify reports size for every frame

    try:
        int(dim.split(",")[0])
    except:
        return [-1, -1]

    return [int(x) for x in dim.split(",")]

def containsIllegalChar(filename):
    #legal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~[]()*+,=/ "
    #for char in filename:
    #    if char not in legal: return False

    # depends on operating system
    if ":" in filename: return True
    return False

def isNotSupportedFile(filepath):
    name, ext = os.path.splitext(filepath)
    legal = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    if ext.lower() in legal:
        return False
    else:
        return True

def file_generator():
    filelist = []
    for root, dirs, files in os.walk(IMAGE_FOLDER, topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_FOLDERS]
        for name in files:
            filelist.append(os.path.join(root, name))
            
    for filepath in filelist:
        if containsIllegalChar(filepath):
            print "ERROR: illegal character found in file'{0}'. Skipping.".format(filepath)
            continue
        if isNotSupportedFile(filepath):
            print "ERROR: Filetype not supported (file'{0})'. Skipping.".format(filepath)
            continue
        # only add files that are not present in the database
        if os.path.isfile(filepath) and not (unicode(filepath, "utf-8"),) in dbFiles:
            width, height = getSize(filepath)
            if width < 0:
                print "ERROR: file {0} is not a valid image file".format(filepath)
                continue
            thumbpath = makeThumb(filepath)            
            print "added file '{0}' to database".format(filepath)
            yield (
                unicode(filepath, "utf-8"),
                width,
                height,
                thumbpath,
            )

c.executemany("""
   INSERT INTO files(filepath, width, height, thumbpath) VALUES (?,?,?,?)""", file_generator())

conn.commit()
c.close()
conn.close()
