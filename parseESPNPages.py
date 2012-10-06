'''
Parsing modules specifically for handling ESPN sports pages (tested only on
NBA data thus far); grabs page @ url and gets pbp / box / extra (all?);
should be called by a function that is iterating over games for a particular
day, and push data to code that transmits it to a db
'''
import sys, os, re
from bs4 import BeautifulSoup as BS
from nltk import clean_html

import genBSandURLtools
from prepworkURL import makePage
from prepworkURL import makeSoup

null_value      = '&nbsp;'
CONTENT_DICT    = {'pbp':('class', 'mod-content'),
                   'box':('id', 'my-players-table')}
EXTRA_LIST      = [('class','game-time-location')]

def processESPNpage(url, ptype):
    '''ptype should be "pbp" or "box" at this point'''
    try:
        data    = getESPNData(url, ptype)
        if data:
            return data
        else:
            print("No %s content found for %s" % (ptype, url))
    except KeyError:
        print("Invalid ptype %s provided" % (ptype))

def getESPNData(url, ptype):
    '''
    Handles which data is being called for; 
    '''
    raw     = makePage(url)
    soup    = makeSoup(raw, url)
    if ptype=='box':
        labels  = CONTENT_DICT[ptype]
        tables  = soup.find_all('div', {labels[0]:labels[1]})
        data    = getESPNbox(tables[0])
    elif ptype=='pbp':
        labels  = CONTENT_DICT[ptype]
        tables  = soup.find_all('div', {labels[0]:labels[1]})
        data    = getESPNpbp(tables[0])
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
    return {'details':details,
            'content':content,
            'playerlinks':playerlink_dict}

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
	temp = line.findAll('a')
	if temp:
            temp    = temp[0]
            if str(temp.get('href')):
		playerlink_dict[str(temp.text)] = str(temp.get('href'))
    return playerlink_dict

# Grabs some Spurs - Nuggets game from spr 2012, gets pbp data, write to file
if __name__=="__main__":

    '''Case for pbp data...'''
    page = "http://espn.go.com/nba/playbyplay?gameId=320223025&period=0"
    print('grabbing page and data..')
    
    data = processESPNpage(page, 'pbp')
    print('data grabbed, writing file...')
    with open('/Users/sinn/Desktop/NBA_TempGame_pbp.txt', 'w') as f1:
        f1.writelines('\t'.join(data['head']) + '\n')
        for line in data['content']:
            f1.writelines('\t'.join(line) + '\n')

##    '''Case for box score data...'''
##    page = "http://scores.espn.go.com/nba/boxscore?gameId=320223025"
##    print('grabbing page and data..')
##
##    
##    data = processESPNpage(page, 'box')
##    #print(data['playerlinks'])
##    print('data grabbed, writing file...')
##    with open('/Users/sinn/Desktop/NBA_TempGame_box_details.txt', 'w') as f1:
##        for line in data['details']:
##            f1.writelines('\t'.join(line) + '\n')
##
##    with open('/Users/sinn/Desktop/NBA_TempGame_box_content.txt', 'w') as f1:
##        for line in data['content']:
##            f1.writelines('\t'.join(line) + '\n')
##
##    with open('/Users/sinn/Desktop/NBA_TempGame_box_playerref.txt', 'w') as f1:
##        playerlinks = data['playerlinks']
##        for key in playerlinks.keys():
##            f1.writelines(key + '\t' + playerlinks[key] + '\n')
    
    print('fine')
