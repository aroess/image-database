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


def getTagsforID(fileID):
    with closing(connection.cursor()) as c:
        sqlString = """
            SELECT tag
            FROM file2tag
            JOIN files ON files.rowid = file2tag.file_id
            JOIN tags ON tags.rowid = file2tag.tag_id
            WHERE files.rowid = ?
        """

        assignedTags = []
        for entry in c.execute(sqlString, (fileID,)):
            assignedTags.append(" ".join(entry).encode('utf-8'))
        assignedTags.sort()

    return assignedTags


def getDimensionsForID(fileID):
    with closing(connection.cursor()) as c:
        sqlString = """SELECT width, height FROM files 
        WHERE rowid = ?"""

        c.execute(sqlString, (fileID,))
        width, height = c.fetchone()

    return  width, height

def getFilepathForID(fileID):
    with closing(connection.cursor()) as c:
        sqlString = """SELECT filepath FROM files 
        WHERE rowid = ?"""

        c.execute(sqlString, (fileID,))
        return c.fetchone()[0]

def isValid(toCheck, param):
    with closing(connection.cursor()) as c:
        if toCheck == "tag":
            c.execute("SELECT tag FROM tags WHERE tag = ?", (param,))
        elif toCheck == "fileID":
            c.execute("SELECT rowid FROM files WHERE rowid = ?", (param,))
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


@route('/edit/<fileID>')
def editTags(fileID):
    assignedTags  = getTagsforID(fileID)
    width, height = getDimensionsForID(fileID)
    filepath      = getFilepathForID(fileID)
    
    return template('edit_image.tpl',
        filename = filepath,
        fileID = fileID,
        assignedTags = assignedTags,
        width = width,
        height = height)


@route('/untagged')
def getUntagged():
    with closing(connection.cursor()) as c:
        sqlString = """SELECT filepath, rowid  FROM files
        WHERE rowid NOT IN (SELECT file_id FROM file2tag)"""

        untaggedFiles = []
        for entry in c.execute(sqlString):
            untaggedFiles.append(
                ["".join(entry[0]).encode('utf-8'),
                     entry[1]])

    return template('untagged.tpl',
        untaggedFiles = untaggedFiles
    )


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
    return static_file(filepath, root='.')

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
        SELECT filepath, thumbpath, files.rowid, COUNT(filepath) as count
        FROM file2tag
        JOIN files ON files.rowid = file2tag.file_id
        JOIN tags ON tags.rowid = file2tag.tag_id
        WHERE {0}
        GROUP BY filepath
        HAVING count = {1}
        LIMIT {2}, {3}
        """.format(tagString, len(tags), lower, OFFSET)
    else:
        sqlString = """
        SELECT filepath, thumbpath, rowid FROM files ORDER BY RANDOM()
        LIMIT {0}, {1}
        """.format(0, OFFSET) 

    print sqlString

    with closing(connection.cursor()) as c:
        resultList = []
        for entry in c.execute(sqlString, tags):
            resultList.append(entry)

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
    fileID = request.POST['fileID']
    tag = request.POST['keywords']
    assignedTags = getTagsforID(fileID)

    if not isValid("fileID", fileID): return

    if not isValid("tag", tag): 
        return {"msg": "Failed. '{0}' is not a valid tag!".format(tag)}

    if tag in assignedTags:
        return {"msg": "Failed. Tag already assinged to image!".format(tag)}

    with closing(connection.cursor()) as c:
        sqlString = """
        INSERT INTO file2tag(file_id, tag_id) VALUES(
            ?,
            (SELECT rowid FROM tags WHERE tag = ?)
        )
        """
        c.execute(sqlString,(fileID, tag))
        connection.commit()

    return {} # return object or callback in $.post will not fire


@route('/deletetagfromimage', method='POST')
def deleteTagFromImage():
    fileID = request.POST['fileID']
    tag    = request.POST['tag']

    with closing(connection.cursor()) as c:
        sqlString = """
            DELETE FROM file2tag WHERE
            tag_id = (SELECT rowid FROM tags WHERE tag = ?) AND
            file_id = ?
            """
        c.execute(sqlString,(tag, fileID))
        connection.commit()

    return {}

@route('/refreshfolder', method='POST')
def refreshfolder():
    out, err  = subprocess.Popen(['python', 'refresh_folder.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate() 
    return {"msg": out }

@route('/deleteimage', method='POST')
def deleteimage():
    fileID = request.POST['fileID']
    with closing(connection.cursor()) as c:
        sqlString = """
            SELECT COUNT(rowid) FROM file2tag WHERE file_id = ?
            """
        count = c.execute(sqlString,(fileID,)).fetchone()[0]

        sqlString = """
            SELECT filepath, thumbpath from files WHERE rowid = ?
            """
        filepath, thumbpath = c.execute(sqlString,(fileID,)).fetchone()

        if count == 0:
            sqlString = """DELETE FROM files WHERE rowid = ?"""
            c.execute(sqlString, (fileID,))
            connection.commit()
            os.remove(os.path.join(filepath))
            os.remove(os.path.join("thumbs", thumbpath))
        else:
            return {"msg":  "Failed. There are still {0} ".format(count) +
                    "keyword(s) attached to this image."}

        return {"msg" : "Image successfully deleted!"}


'''
END DB FUNCTIONS
'''

run(host='localhost', port=8080)
