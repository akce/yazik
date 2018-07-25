"""
Yazik main module.
Copyright (c) 2018 Acke, see LICENSE file for allowable usage.
"""
import sys
import time

def authoradd(db, name):
    """ Add a new author to db. """
    q = '''INSERT OR IGNORE INTO author (name) VALUES (?)'''
    newid = insert(db, q, name)
    if newid:
        db.commit()
    return newid

def authorlist(db, name=None):
    where, value = wherelike(name=name)
    query = 'SELECT * FROM author ' + where
    with db as cur:
        res = cur.execute(query, value)
        rows = res.fetchall()
    return rows

def bookadd(db, title, authorname=None):
    if authorname is None:
        aid = None
    else:
        authors = authorlist(db, name=authorname)
        if len(authors) == 1:
            aid = authors[0]['authorid']
        elif len(authors) == 0:
            raise Exception('No matches for author "{}" found'.format(authorname))
        else:
            raise Exception('Author name "{}" has multiple matches {}'.format(authorname, sorted(a['name'] for a in authors)))
    query = 'INSERT INTO book (title, authorid, whenadded) VALUES (?, ?, ?)'
    newid = insert(db, query, title, aid, int(time.time()))
    if newid:
        db.commit()
    return newid

def booklist(db, title=None):
    where, value = wherelike(title=title)
    query = 'SELECT * FROM book ' + where
    with db as cur:
        res = cur.execute(query, value)
        rows = res.fetchall()
    return rows

def wordadd(db, word, booktitle=None, page=None):
    wordid = insert(db, 'INSERT OR IGNORE INTO word (word) VALUES (?)', word)
    if wordid is None:
        # Word exists in db, try and find the existing entry.
        words = wordlist(db, word)
        if len(words) == 1:
            wordid = words[0]['wordid']
        elif len(words) == 0:
            raise Exception('Insert word "{}" failed'.format(word))
        else:
            raise Exception('Word "{}" has multiple matches {}'.format(word, sorted(w['word'] for w in words)))
    ### Add a seen entry for the word.
    ## Try and link the seen entry to a book.
    if booktitle is None:
        # Grab the last book added to 'book' table and use that if booktitle is not provided.
        book = getlast(db, table='book')
        if book is None:
            bookid = None
        else:
            bookid = book['bookid']
    else:
        books = booklist(db, title=booktitle)
        if len(books) == 1:
            bookid = books[0]['bookid']
        elif len(books) == 0:
            raise Exception('No matches for "{}"'.format(book))
        else:
            raise Exception('Book "{}" has multiple matches {}'.format(book, sorted(b['book'] for b in books)))
    seenid = insert(db, 'INSERT INTO seen (wordid, bookid, page, whenseen) VALUES (?, ?, ?, ?)', wordid, bookid, page, int(time.time()))
    if wordid and seenid:
        db.commit()
    return wordid, seenid

def wordlist(db, word=None):
    where, value = wherelike(word=word)
    query = 'SELECT * FROM word ' + where
    with db as cur:
        res = cur.execute(query, value)
        rows = res.fetchall()
    return rows

def definitionadd(db, definition, word=None, force=False):
    if word is None:
        try:
            wordid = getlast(db, table='word')['wordid']
        except TypeError:
            raise Exception('No word for definition found') from None
    else:
        # Try and find *one* matching word.
        words = wordlist(db, word)
        if len(words) == 1:
            wordid = words[0]['wordid']
        elif len(words) == 0:
            raise Exception('Word "{}" not found'.format(word))
        else:
            raise Exception('Word "{}" has multiple matches {}'.format(word, sorted(w['word'] for w in words)))
    # See if there's already a definition for word, will update it if force is True.
    olddef = definitionget(db, wordid)
    if olddef is None:
        # Add the new definition.
        newid = insert(db, 'INSERT INTO definition (wordid, definition) VALUES (?, ?)', wordid, definition)
    else:
        if force is True:
            oldid = olddef['definitionid']
            insert(db, 'UPDATE definition SET definition = ? WHERE wordid = ?', definition, oldid)
            newid = oldid
        else:
            raise Exception("Word already has a definition. Add --force to change definition.")
    db.commit()
    return newid

def definitionget(db, wordid):
    query = 'SELECT * FROM definition WHERE wordid = ?'
    with db as cur:
        res = cur.execute(query, (wordid,))
        row = res.fetchone()
    return row

def getlast(db, table):
    query = 'SELECT * from {t} ORDER BY {t}id DESC LIMIT 1'.format(t=table)
    with db as cur:
        res = cur.execute(query)
        row = res.fetchone()
    return row

def wherelike(**kwargs):
    wl = []
    value = []
    for k, v in kwargs.items():
        if v is not None:
            wl.append('{} LIKE ?'.format(k))
            value.append('%{}%'.format(v))
    if wl:
        where = ' WHERE ' + ' OR '.join(wl)
    else:
        where = ''
    return where, value

def insert(db, query, *values):
    with db as cur:
        res = cur.execute(query, values)
        if res.rowcount == 0:
            # Assume we've hit a duplicate entry.
            newid = None
        else:
            newid = res.lastrowid
    return newid
