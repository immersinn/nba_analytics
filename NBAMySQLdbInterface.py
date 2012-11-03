#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

import MySQLdb

'''
Create connection to the MySQL --> NBA database
use option files, where option file in in MySQL format for vars:
import os
option_file = os.environ["HOME"] + '/' + file_name
conn = ms.connect(db = name, read_default_file = option_file)
default is no args...
'''
def handcon(db='', h='', p='', u=''):
    try:
        conn = ms.connect(db        = db,
                          host      = h,
                          user      = u,
                          passwd    = p)
        print "Connected"
    except ms.Error, e:
        print 'Connection failed'
        print 'Error code: ', e.args[0]
        print 'Error message: ', e.args[1]
        sys.exit(1)
    else:
        return conn

def makeConn():
    '''
    Connect to NBA_temp db
    '''
    conn = connect.handcon(db   = 'NBA_temp',
                           h    = 'localhost',
                           u    = 'sinn',
                           p    = 't')
    return conn


'''
Handles the general call to the fucntions for updating the
MySQL database with new information;
'''
def addInfo(pageType,cursor,data):
    if pageType=='pbp':

    elif pageType=='box':
        updateBox(cursor, data)

    elif pageType=='ext':

    else:
        print "Warning! non valid page type; not updating"

'''
Update general game info, e.g., MDB id's for game data;
'''
def updateGameInfo(cursor, data):
    '''
    Data should be from box['playerlinks']; dictionary-ize it;
    Layout for players_site table:
    +---------------+------------------+------+-----+---------+----------------+
    | Field         | Type             | Null | Key | Default | Extra          |
    +---------------+------------------+------+-----+---------+----------------+
    | game_id       | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
    | espn_gid      | int(10) unsigned | NO   |     | NULL    |                |
    | game_date     | date             | NO   |     | NULL    |
    | pbp_mdb_id    | varchar(24)      | NO   |     | NULL    |                |
    | box_mdb_id    | varchar(24)      | NO   |     | NULL    |                |
    | ext_mdb_id    | varchar(24)      | NO   |     | NULL    |                |
    | season        | varchar(7)      | NO   |     | NULL    |                |
    +---------------+------------------+------+-----+---------+----------------+

    '''
    data_list = [(int(ga['id']),
                  ga['date'],
                  ga['pbp_id'],
                  ga['box_id'],
                  ga['ext_id'],
                  ga['season']) for ga in data]
    cursor.executemany(
        """INSERT INTO game_mdb_ref (espn_gid,
                                     game_date,
                                     pbp_mdb_id,
                                     box_mdb_id,
                                     ext_mdb_id,
                                     season)
            VALUES(%s, %s, %s, %s, $s, $s)""", data_list) 


'''
Handles connection to db with general player info (ESPN ID,
Web Page, etc.;
'''
def addPlayers2PS(cursor, data):
    '''
    Data should be from box['playerlinks']; dictionary-ize it;
    Layout for players_site table:
    +---------------+------------------+------+-----+---------+----------------+
    | Field         | Type             | Null | Key | Default | Extra          |
    +---------------+------------------+------+-----+---------+----------------+
    | player_id     | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
    | espn_id       | int(10) unsigned | NO   |     | NULL    |                |
    | last_name     | varchar(30)      | NO   |     | NULL    |                |
    | first_name    | varchar(30)      | NO   |     | NULL    |                |
    | pbp_name      | varchar(50)      | NO   |     | NULL    |                |
    | espn_web_page | varchar(150)     | NO   |     | NULL    |                |
    +---------------+------------------+------+-----+---------+----------------+

    Don't need to input player_id, automatically done
    '''
    data_list = [(int(pl['id']),
                 pl['last'],
                 pl['first'],
                 pl['pbp_name'],
                 pl['web_page']) for pl in data]

    cursor.executemany(
            """INSERT INTO players_site (espn_id,
                                         last_name,
                                         first_name,
                                         pbp_name,
                                         espn_web_page)
               VALUES(%s, %s, %s, %s, %s)""", data_list)
##    for pl in data:
##        addPlayer2PS(cursor, pl)

def addPlayer2PS(cursor, pl):
    pl = (int(pl['id']),
               pl['last'],
               pl['first'],
               pl['pbp_name'],
               pl['web_page'])
    cursor.execute(
            """INSERT INTO players_site (espn_id,
                                         last_name,
                                         first_name,
                                         pbp_name,
                                         espn_web_page)
               VALUES(%s, %s, %s, %s, %s)""", pl)
