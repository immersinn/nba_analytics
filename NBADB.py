'''
SOON TO CHANGE --> WILL REF INTERFACE CLASS OBJECTS FOR SQL, MDB

Handles placing data from ESPN pages into MySQL and MongoDB;
SQL for standard relational stuff (players in game xxx);
Mongo for structured doc stuff (pbp, raw box score pages);

'''
import sys, os

import NBAMySQLdbInterface as sqlI
import NBAMongodbInterface as mdbI

def NBADBHandle(pbp=None,box=None,ext=None):
    '''
    These are all multi-game dictionaries, where each
    entry is the pbp / box / ext for the given game;
    '''
    if pbp:
        db = sqlI.makeConn()
        with db:
            cursor = db.cursor()
            for key in pbp.keys()
            sqlI.addInfo('pbp',cursor,pbp)

    if box:
        db = sqlI.makeConn()
        with db:
            cursor = db.cursor()
            for key in box.keys()
            sqlI.addInfo('box',cursor,pbp)

    if ext:
        db = sqlI.makeConn()
        with db:
            cursor = db.cursor()
            for key in ext.keys()
            sqlI.addInfo('ext',cursor,pbp)
