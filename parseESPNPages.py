# -*- coding: utf-8 -*-
'''
Parsing modules specifically for handling ESPN sports pages (tested only on
NBA data thus far); grabs page @ url and gets pbp / box / extra (all?);
should be called by a function that is iterating over games for a particular
day, and push data to code that transmits it to a db
'''
import sys, os
import re

from bs4 import BeautifulSoup as BS
from nltk import clean_html

from webpage_parse.soupypages import soupFromUrl

null_value      = '&nbsp;'
CONTENT_DICT    = {'pbp':('class', 'mod-content'),
                   'box':('id', 'my-players-table')}
EXTRA_LIST      = [('class','game-time-location')]

def processESPNPage(url, ptype):
    '''ptype should be "pbp" or "box" at this point'''
    try:
        data    = getESPNData(url, ptype)
        if data:
            return data
        else:
            print("No %s content found for %s" % (ptype, url))
    except KeyError:
        print("Invalid ptype %s provided" % (ptype))

def processESPNShotsPage(url):
    '''
    Handles grabbing the x,y coords from the ESPN shots page;
    returns a dict;
    '''
    shotSoup = soupFromUrl(url, parser='xml')['soup']
    shots = shotSoup.findAll('Shot')
    shotDict = getESPNShotDict(shots)
    return shotDict

def getESPNData(url, ptype):
    '''
    Handles which data is being called for; 
    '''
    soup    = soupFromUrl(url, hdr=True)['soup']
    if ptype=='box':
        labels  = CONTENT_DICT[ptype]
        tables  = soup.find_all('div', {labels[0]:labels[1]})
        data    = getESPNbox(tables[0])
    elif ptype=='pbp':
        labels  = CONTENT_DICT[ptype]
        if 'Play-By-Play not available' in soup.text:   #nfid
            data = {'head':'No PBP data for game', 'content':"!!!!!!"}
        else: 
            tables  = soup.find_all('div', {labels[0]:labels[1]})
            data    = getESPNpbp(tables[1])     # check this plz
    elif ptype=='extra':
        if raw: text = getText(raw)
        else: text = ''
        data    = getESPNext(soup, EXTRA_LIST)
        data['text'] = text
    return data

def getESPNext(soup, attrs):
    '''Really just the recaps page, but also will grab extra info here as well'''
    data = dict()
    for (attr,name) in attrs:
        data[attr] = soup.find_all('div', {attr:name})
    return data

def getESPNpbp(table):
    '''
    url is a play-by-play url obtained from score-summary ESPN page;
    use BeautifulSoup to parse apart data_in; all relevant data found
    in 'table' HTML structures, hence we grab those;
    '''
        
    pbp         = table.findAll('tr')
    '''Use BS to get the headers (e.g., home and away team for game)'''
    header      = [str(h.text) for h in pbp[1].findAll('th')]
    content     = []
    for line in pbp[2:]:
        temp    = line.findAll('td')
        content.append([str(e.text.encode('utf8')) for e in temp])
    return {'head':header, 'content':content}

def getESPNbox(table):
    '''
    url is a box score url obtained from score-summary ESPN page;
    use BeautifulSoup to parse apart data_in; all relevant data found
    in 'table' HTML structures, hence we grab those;
    '''
    summary     = table.findAll('tr')
    details     = []
    content     = []
    for line in summary:
        '''
        "details" are headers, teams stuff;
        "content" is actual player data;
        '''
        details.append([str(h.text.encode('utf8')) for h in line.findAll('th')])
        content.append([str(h.text.encode('utf8')) for h in line.findAll('td')])
    playerlink_dict = getESPNplayerlinks(summary)
    refined_pl_dict = refineESPNplayerlinks(playerlink_dict)
    return {'details':details,
            'content':content,
            'playerlinks':playerlink_dict,
            'ref_pls':refined_pl_dict}

def getESPNShotDict(shots):
    '''
    Components of the shot:
    d       --> pbp-esq discription (Made 19ft jumper 11:44 in 1st Qtr."
    id      --> the shot id (gameID+xxxxx)
    made    --> T/F
    p       --> player shooting (same as pbp name)
    pid     --> player ID (super usefull)
    qtr     --> quarter (what does OT look like??)
    t       --> values: a(way), h(ome)
    x       --> x-cord where shot was taken from
    y       --> y-cord where shot was taken from

    I'm assuming this holds (from basketballgeek.com/data)
    How do I interpret the (x,y) shot location coordinates?:
    If you are standing behind the offensive team’s hoop then
    the X axis runs from left to right and the Y axis runs from
    bottom to top. The center of the hoop is located at (25, 5.25).
    x=25 y=-2 and x=25 y=96 are free-throws (8ft jumpers)
    '''

    '''Transform into a dictionary; worry about matching up to pbp later...'''
    ShotDict = {}
    for s in shots:
        ShotDict[s['id']] = \
                          {'Q':s['qtr'],
                           'time' : s['d'].split(' ')[3],
                           'made' : u'0' if s['made']=='false' else u'1',
                           'pts' : u'2' if s['d'].find('jumper')>-1 else u'3',
                           'p' : s['p'],
                           'pid' : s['pid'],
                           't' : s['t'],
                           'x' : s['x'],
                           'y' : s['y']}
    return ShotDict

def getText(raw):
    '''Gets same summary text from recap page'''
    text_start = "<!-- begin recap text -->"    # these are super handy
    text_stops = "<!-- end recap text -->"
    text = raw[raw.find(text_start)+len(text_start):\
               raw.find(text_stops)]
    text = clean_html(text)
    return text

def getESPNplayerlinks(summary):
    '''
    Gets the ESPN page urls for players in the game from the box score page;
    keys are the full names of players used in box score, and values are
    the urls;
    '''
    playerlink_dict = dict()
    for line in summary:
	temp = line.findAll('a')    # returns a list of finds;
	'Make sure soemthing found on the line, not []'
	if temp:
            temp = temp[0]          # sound be only 1 element
            if str(temp.get('href')) != 'None':     # not team name...
                playerlink_dict[str(temp.text)] = str(temp.get('href'))
    return playerlink_dict

def refineESPNplayerlinks(playerlink_dict):
    '''
    Takes info from playerlink_dict and turns it into dict
    for importing data into "
    players_site" MySQL table;
    '''
    refined_pl_dict = list()
    for key in playerlink_dict.keys():
        temp = dict()
        temp['first']   = ' '.join(key.split(' ')[:-1])
        temp['last']    = key.split(' ')[-1]
        temp['id']      = playerlink_dict[key].split('/')[-2]
        temp['pbp_name'] = ' '.join(playerlink_dict[key].split('/')[-1].split('-'))
        temp['web_page'] = playerlink_dict[key]
        refined_pl_dict.append(temp.copy())
    return refined_pl_dict
        
        

# Grabs some Spurs - Nuggets game from spr 2012, gets pbp data, write to file
if __name__=="__main__":

    '''Set the correct directory'''
    if os.path.isdir('/home/immersinn/NBA-Data-Stuff'):     #delldesk
        default_path = '/home/immersinn/NBA-Data-Stuff'
    elif os.path.isdir('/Users/sinn/NBA-Data-Stuff'):
        defualt_path = '/home/immersinn/NBA-Data-Stuff'

    '''Case for pbp data...'''
    page = "http://espn.go.com/nba/playbyplay?gameId=320223025&period=0"
    print('grabbing page and data..')
    
    data = processESPNpage(page, 'pbp')
    print('data grabbed, writing file...')
    with open(os.path.join(default_path, 'DataFiles/TestOut/NBA_TempGame_pbp.txt'),
              'w') as f1:
        f1.writelines('\t'.join(data['head']) + '\n')
        for line in data['content']:
            f1.writelines('\t'.join(line) + '\n')

    '''Case for box score data...'''
    page = "http://scores.espn.go.com/nba/boxscore?gameId=320223025"
    print('grabbing page and data..')
    
    data = processESPNpage(page, 'box')
    #print(data['playerlinks'])
    
    print('data grabbed, writing file...')
    with open('/Users/sinn/Desktop/NBA_TempGame_box_details.txt', 'w') as f1:
        for line in data['details']:
            f1.writelines('\t'.join(line) + '\n')

    with open('/Users/sinn/Desktop/NBA_TempGame_box_content.txt', 'w') as f1:
        for line in data['content']:
            f1.writelines('\t'.join(line) + '\n')

    with open('/Users/sinn/Desktop/NBA_TempGame_box_playerref.txt', 'w') as f1:
        playerlinks = data['playerlinks']
        for key in playerlinks.keys():
            f1.writelines(key + '\t' + playerlinks[key] + '\n')
    
    print('fine')
