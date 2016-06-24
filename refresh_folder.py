import os, subprocess, sys, sqlite3

conn = sqlite3.connect('imagetag.sqlite') 
c = conn.cursor()

c.execute("select filename from files")
dbFiles = c.fetchall()

def makeThumb(filename):
    cmd = """
    convert "img/{0}"[0] -thumbnail 100x100^ -gravity center -crop \
    100x100+0+0  +repage img/thumbs/"{1}.jpg"
    """.format(filename, os.path.splitext(os.path.basename(filename))[0])
    os.system(cmd)

def getSize(path):
    dim = subprocess.Popen(["identify","-format","%w,%h;", path], 
        stdout=subprocess.PIPE).communicate()[0]
    dim = dim.split(";")[0] # identify reports size for every frame
    return [int(x) for x in dim.split(",")]

def containsIllegalChar(file):
    legal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~[]()*+,="
    for char in file:
        if char not in legal: return True
    return False

def file_generator():
    for file in os.listdir("img"):
        if containsIllegalChar(file):
            print "ERROR: illegal character found in file'{0}'. Skipping.".format(file)
            continue
        # only add files that are not present in the database
        if os.path.isfile(os.path.join("img", file)) and not (file,) in dbFiles:
            width, height = getSize(os.path.join("img", file))
            makeThumb(file)
            print "added file '{0}' to database".format(file)
            yield (file, width, height,)

c.executemany("""
   INSERT INTO files(filename, width, height) VALUES (?,?,?)""", file_generator())

conn.commit()
c.close()
conn.close()
