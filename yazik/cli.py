"""
Command line interface module.
Copyright (c) 2018 Acke, see LICENSE file for allowable usage.
"""

import argparse
import os

from . import db
from . import nestedarg
from . import yazik

def usedb(func):
    def mkdb(args):
        dbobj = db.DB(args.dbfile)
        return func(dbobj, args)
    return mkdb

def nonestr(argslist):
    # argslist == [] is the default for nargs="*" arguments.
    if argslist is None or argslist == []:
        ret = None
    else:
        ret = " ".join(argslist)
    return ret

@usedb
def authoradd(dbobj, args):
    name = ' '.join(args.name)
    newid = yazik.authoradd(db=dbobj, name=name)
    if newid is not None:
        print('{:3}: {}'.format(newid, name))

@usedb
def authorlist(dbobj, args):
    searchname = nonestr(args.name)
    authors = yazik.authorlist(db=dbobj, name=searchname)
    for a in authors:
        print('{:3}: {}'.format(a['authorid'], a['name']))

@usedb
def bookadd(dbobj, args):
    yazik.bookadd(db=dbobj, title=nonestr(args.title), authorname=nonestr(args.authorname))

@usedb
def booklist(dbobj, args):
    searchtitle = nonestr(args.title)
    books = yazik.booklist(db=dbobj, title=searchtitle)
    for b in books:
        print('{:3}: {}'.format(b['bookid'], b['title']))

@usedb
def wordadd(dbobj, args):
    wordid, _ = yazik.wordadd(db=dbobj, word=args.word, booktitle=nonestr(args.booktitle), page=args.page)
    # Search for an existing definition.
    worddef = yazik.definitionget(db=dbobj, wordid=wordid)
    if worddef is None:
        print('No definition for word "{}"'.format(args.word))
    else:
        print(worddef['definition'])

@usedb
def wordlist(dbobj, args):
    words = yazik.wordlist(db=dbobj, word=args.word)
    for w in words:
        worddef = yazik.definitionget(db=dbobj, wordid=w['wordid'])
        if worddef is None:
            d = None
        else:
            d = worddef['definition']
        print('{:3}: {:15} {}'.format(w['wordid'], w['word'], d))

@usedb
def definitionadd(dbobj, args):
    defstr = nonestr(args.definition)
    definitionid = yazik.definitionadd(db=dbobj, definition=defstr, word=args.word, force=args.force)

def main():
    dbfile = os.path.join(os.path.expanduser('~'), '.yazik.db')
    parser = argparse.ArgumentParser()
    parser.add_argument('--dbfile', default=dbfile, help='db file. Default: %(default)s')
    command = nestedarg.NestedSubparser(parser.add_subparsers())
    with command('author', aliases=['a'], help='authors') as c:
        subcommand = nestedarg.NestedSubparser(c.add_subparsers())
        with subcommand('add', aliases=['a'], help='add new author') as s:
            s.add_argument('name', nargs='+', help='name of author')
            s.set_defaults(command=authoradd)
        with subcommand('ls', aliases=['l'], help='list authors') as s:
            s.add_argument('name', nargs='*', help='display authors matching name only')
            s.set_defaults(command=authorlist)
    with command('book', aliases=['b'], help='books') as c:
        subcommand = nestedarg.NestedSubparser(c.add_subparsers())
        with subcommand('add', aliases=['a'], help='add new book') as s:
            s.add_argument('title', nargs='+', help='title of book')
            s.add_argument('--authorname', nargs='+', help='name of author')
            s.set_defaults(command=bookadd)
        with subcommand('ls', aliases=['l'], help='list books') as s:
            s.add_argument('title', nargs='*', default=None, help='title of book')
            s.set_defaults(command=booklist)
    with command('word', aliases=['w'], help='words') as c:
        subcommand = nestedarg.NestedSubparser(c.add_subparsers())
        with subcommand('add', aliases=['a'], help='add new word') as s:
            s.add_argument('word', help='the word')
            s.add_argument('--definition', nargs='+', help='initial definition of word')
            s.add_argument('--booktitle', nargs='+', help='title of book')
            s.add_argument('--page', type=int, help='page number of book')
            s.set_defaults(command=wordadd)
        with subcommand('ls', aliases=['l'], help='list words') as s:
            s.add_argument('word', nargs='?', help='optional search word')
            s.set_defaults(command=wordlist)
        with subcommand('def', aliases=['d'], help='set definition for word') as s:
            s.add_argument('definition', nargs='+', help='definition of a word')
            s.add_argument('--word', help='the word')
            s.add_argument('--force', default=False, action='store_true', help='force definition update. Default: %(default)s')
            s.set_defaults(command=definitionadd)
    args = parser.parse_args()
    args.command(args)
