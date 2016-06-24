#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from bottle import *
import os, re, json, subprocess

from contextlib import closing
from dbmod import connection

# https://en.wikipedia.org/wiki/Prepared_statement#Python_DB-API
# https://stackoverflow.com/questions/8630423/automate-opening-and-closing-the-database-connection

'''
HELPER FUNCTIONS
'''
def writeTagList():
    with closing(connection.cursor()) as c:
        sqlString = "SELECT tag FROM tags"
        allTags = []
        for entry in c.execute(sqlString):
            allTags.append(" ".join(entry).encode('utf-8'))
        allTags.sort()

    with open("tags.json", "w") as f:
        f.write(json.dumps(allTags))


def getTagsforFilename(filename):
    with closing(connection.cursor()) as c:
        sqlString = """
            SELECT tag
            FROM file2tag
            JOIN files ON files.rowid = file2tag.file_id
            JOIN tags ON tags.rowid = file2tag.tag_id
            WHERE filename = ?
        """

        assignedTags = []
        for entry in c.execute(sqlString, (filename,)):
            assignedTags.append(" ".join(entry).encode('utf-8'))
        assignedTags.sort()

    return assignedTags


def getDimensionsForFilename(filename):
    with closing(connection.cursor()) as c:
        sqlString = """SELECT width, height FROM files 
        WHERE filename=?"""

        c.execute(sqlString, (filename,))
        width, height = c.fetchone()

    return  width, height
    

def isValid(toCheck, param):
    with closing(connection.cursor()) as c:
        if toCheck == "tag":
            c.execute("SELECT tag FROM tags WHERE tag = ?", (param,))
        elif toCheck == "filename":
            c.execute("SELECT filename FROM files WHERE filename = ?", (param,))
        else:
            raise NameError

        try:
            if c.fetchone() is None:
                print param + " is not a valid " + toCheck
                return False
        except: pass

    return True

'''
END HELPER FUNCTIONS
'''

'''
TEMPLATES
'''
@route('/')
def index():
    return template('search.tpl')


@route('/edittags')
def addkeys():
    with closing(connection.cursor()) as c:
        sqlString = "SELECT tag FROM tags"
        allTags = []
        for entry in c.execute(sqlString):
            allTags.append(" ".join(entry).encode('utf-8'))
        allTags.sort()

    return template('edit_tags.tpl',
        allTags = allTags)


@route('/edit/<filename>')
def editTags(filename):
    assignedTags = getTagsforFilename(filename)
    width, height = getDimensionsForFilename(filename)

    return template('edit_image.tpl',
        filename = filename,
        assignedTags = assignedTags,
        width = width,
        height = height)


@route('/untagged')
def getUntagged():
    with closing(connection.cursor()) as c:
        sqlString = """SELECT filename  FROM files
        WHERE rowid NOT IN (SELECT file_id FROM file2tag)"""

        untaggedFiles = []
        for entry in c.execute(sqlString):
            untaggedFiles.append(" ".join(entry).encode('utf-8'))

    return template('untagged.tpl',
        untaggedFiles = untaggedFiles)


@route('/tagcount')
def tagCount():
    with closing(connection.cursor()) as c:
        sqlString = """
        SELECT  tag, COUNT(tag_id) AS count  FROM file2tag 
        JOIN tags ON file2tag.tag_id = tags.rowid
        GROUP BY tag_id
        ORDER BY count DESC"""

        tagcount = c.execute(sqlString)
        tagcount = tagcount.fetchall()
    
    return template('tagcount.tpl',
        tagcount = tagcount)


@route('/refresh')
def refresh():
    return template('refresh.tpl')



@route('/static/<filepath:path>')
def serveStatic(filepath):
    return static_file(filepath, root='')

'''
END TEMPLATES
'''

'''
DB FUNCTIONS
'''
@route('/search', method='POST')
def searchFiles():
    try: # check for strange page indices
        pIndex = int(request.POST['pageCount']) # page index
    except:
        pIndex = 0

    OFFSET = int(request.POST['offset'])
    lower = str(pIndex*OFFSET)

    tags = request.POST['searchKey'].split(',')
    tags = filter(None, tags)

    if tags:
        tagString = ""
        for tag in tags: tagString += "tag = ? OR "
        tagString = tagString[:-3] # delete last OR

        sqlString = """
        SELECT filename, COUNT(filename) as count
        FROM file2tag
        JOIN files ON files.rowid = file2tag.file_id
        JOIN tags ON tags.rowid = file2tag.tag_id
        WHERE {0}
        GROUP BY filename
        HAVING count = {1}
        LIMIT {2}, {3}
        """.format(tagString, len(tags), lower, OFFSET)
    else:
        sqlString = """
        SELECT filename FROM files ORDER BY RANDOM()
        LIMIT {0}, {1}
        """.format(0, OFFSET) 

    print sqlString

    with closing(connection.cursor()) as c:
        resultList = []
        for entry in c.execute(sqlString, tags):
            resultList.append(entry[0])

    return {"result": resultList}


@route('/addtagtodb', method='POST')
def addtagToDB():
    tag = request.POST['newkey']
    if not tag:
        print "keyword empty"
        return

    with closing(connection.cursor()) as c:
        dbTags = []
        for entry in c.execute("select tag from tags"):
            dbTags.append(" ".join(entry).encode('utf-8'))

        if not tag in dbTags:
            c.execute("""
            INSERT INTO tags(tag) VALUES(?)""", (tag,))
            connection.commit()
            writeTagList()
        else:
            return {"msg" : "Failed. Tag already in database."}
            
    return {} # return object or callback in $.post will not fire


@route('/deletetagfromdb', method='POST')
def deleteTagFromDB():
    tag = request.POST['removekey']
    if not tag: return

    with closing(connection.cursor()) as c:
        sqlString = """SELECT COUNT(rowid) FROM file2tag WHERE tag_id = 
                   (SELECT rowid FROM tags WHERE tag=?)"""

        count = c.execute(sqlString, (tag,))
        count = c.fetchone()[0]

        if count == 0:
            sqlString = """DELETE FROM tags WHERE tag=?"""
            c.execute(sqlString, (tag,))
            connection.commit()
            writeTagList()
        else:
            return {"msg":  "Failed. There are still {0} ".format(count) +
                    "file(s) tagged with this keyword."}

    return {} # return object or callback in $.post will not fire


@route('/addtagtoimage', method='POST')
def addTagstoImage():
    filename = request.POST['filename']
    tag = request.POST['keywords']
    assignedTags = getTagsforFilename(filename)

 
    if not isValid("filename", filename): return

    if not isValid("tag", tag): 
        return {"msg": "Failed. '{0}' is not a valid tag!".format(tag)}

    if tag in assignedTags:
        return {"msg": "Failed. Tag already assinged to image!".format(tag)}

    with closing(connection.cursor()) as c:
        sqlString = """
        INSERT INTO file2tag(file_id, tag_id) VALUES(
            (SELECT rowid FROM files WHERE filename = ?),
            (SELECT rowid FROM tags WHERE tag = ?)
        )
        """
        c.execute(sqlString,(filename, tag))
        connection.commit()

    return {} # return object or callback in $.post will not fire


@route('/deletetagfromimage', method='POST')
def deleteTagFromImage():
    filename = request.POST['filename']
    tag = request.POST['tag']

    with closing(connection.cursor()) as c:
        sqlString = """
            DELETE FROM file2tag WHERE
            tag_id = (SELECT rowid FROM tags WHERE tag = ?) AND
            file_id = (SELECT rowid FROM files WHERE filename = ?)
            """
        c.execute(sqlString,(tag, filename))
        connection.commit()

    return {}

@route('/refreshfolder', method='POST')
def refreshfolder():
    out, err  = subprocess.Popen(['python', 'refresh_folder.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate() 
    return {"msg": out }

@route('/deleteimage', method='POST')
def deleteimage():
    filename = request.POST['filename']
    with closing(connection.cursor()) as c:
        sqlString = """
            SELECT COUNT(rowid) FROM file2tag WHERE file_id = 
            (SELECT rowid FROM files WHERE filename=?)
            """

        count = c.execute(sqlString,(filename,))
        count = c.fetchone()[0]

        if count == 0:
            sqlString = """DELETE FROM files WHERE filename=?"""
            c.execute(sqlString, (filename,))
            connection.commit()
            os.remove(os.path.join("img", filename))
            filename = os.path.splitext(filename)[0]
            os.remove(os.path.join("img", "thumbs", filename + ".jpg"))
        else:
            return {"msg":  "Failed. There are still {0} ".format(count) +
                    "keyword(s) attached to this image."}

        return {"msg" : "Image successfully deleted!"}


'''
END DB FUNCTIONS
'''

run(host='localhost', port=8080)
