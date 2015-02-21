# -*- coding: utf-8 -*-
'''
Parsing modules specifically for handling ESPN sports pages (tested only on
NBA data thus far); grabs page @ url and gets pbp / box / extra (all?);
should be called by a function that is iterating over games for a particular
day, and push data to code that transmits it to a db
'''
import re

from bs4 import BeautifulSoup as BS
from nltk import clean_html

null_value      = '&nbsp;'
empty_str_filter = lambda x: x not in ['', '\xc2\xa0']


#////////////////////////////////////////////////////////////
#{ Set and Get content
#////////////////////////////////////////////////////////////


def espnRecapFromSoup(soup, attrs):
    """
    Really just the recaps page, but also will grab extra info here as well
    """
    if raw:
        text = getText(raw)
    else:
        text = ''
    data = dict()
    for (attr,name) in attrs:
        data[attr] = soup.find_all('div', {attr:name})
    return data


def getText(raw):
    '''Gets same summary text from recap page'''
    text_start = "<!-- begin recap text -->"    # these are super handy
    text_stops = "<!-- end recap text -->"
    text = raw[raw.find(text_start)+len(text_start):\
               raw.find(text_stops)]
    text = clean_html(text)
    return text


#////////////////////////////////////////////////////////////
#{ process the box score nba page
#////////////////////////////////////////////////////////////


def espnBoxFromSoup(soup, labels, game_id):
    """
    url is a box score url obtained from score-summary ESPN page;
    use BeautifulSoup to parse apart data_in; all relevant data found
    in 'table' HTML structures, hence we grab those;

        "details" are headers, teams stuff;
        "content" is actual player data;

    """
    summary = espnSummaryFromBox(soup, labels)
    player_info = espnPlayerInfoFromBox(summary, game_id)
    game_info = espnGameInfoFromBox(summary, player_info)
    return {'player_info':player_info,
            'game_info':game_info}


def espnSummaryFromBox(soup, labels):
    """Extract important table from Box Soup"""
    tables  = soup.find_all('div', {labels[0]:labels[1]})
    summary = tables[0].findAll('tr')
    return summary


def headerAndContentFromBox(summary):
    details     = []
    content     = []
    for line in summary:
        details.append([str(h.text.encode('utf8')) for h in line.findAll('th')])
        content.append([str(h.text.encode('utf8')) for h in line.findAll('td')])
    return details, content


def startIndex(details):
    start_index = [i for i in range(len(details)) if \
                   details[i] and details[i][0]=='STARTERS']
    return start_index


def benchIndex(details):
    bench_index = [i for i in range(len(details)) if \
                   details[i] and details[i][0]=='BENCH']
    return bench_index


def totalsIndex(details):
    totals_index = [i for i in range(len(details)) if \
                    details[i] and details[i][0]=='TOTALS']
    return totals_index


def espnPlayerInfoFromBox(summary, game_id):
    """
    Gets the ESPN page urls for players in the game from the box score page;
    keys are the full names of players used in box score, and values are
    the urls;

    does there need to be a "try" here?
    """
    player_links = playerLinksFromBox(summary)
    player_stats = playerStatsFromBox(summary)
    player_data = {}
    for pid, info in player_links.items():
        temp = {}
        temp['meta'] = info
        temp['stats'] = player_stats[info['name']]
        temp['stats']['game_id'] = game_id
        player_data[pid] = temp
    return player_data


def playerLinksFromBox(summary):
    playerlink_dict = dict()
    for line in summary:
        try:
            temp = line.findAll('a')[0]
            if str(temp.get('href')) != 'None':     # not team name...
                player_info = refineEspnPlayerlink(str(temp.text),
                                                   str(temp.get('href')))
                playerlink_dict[player_info['id']] = player_info
        except IndexError:
            pass
    return playerlink_dict


def refineEspnPlayerlink(name, value):
    """
    Takes info from playerlink_dict and turns it into dict
    for importing data into "
    players_site" MySQL table;
    """
    temp = dict()
    temp['name']        = name
    temp['first']       = ' '.join(name.split(' ')[:-1])
    temp['last']        = name.split(' ')[-1]
    temp['id']          = value.split('/')[-2]
    temp['pbp_name']    = ' '.join(value.split('/')[-1].split('-'))
    temp['web_page']    = value
    return temp


def playerStatsFromBox(summary):
    """

    """
    details, content = headerAndContentFromBox(summary)
    starters_index = startIndex(details)
    bench_index = benchIndex(details)
    totals_index = totalsIndex(details)
    players_fields = filter(empty_str_filter,
                            details[starters_index[0]][1:])
    players_fields = [pf.strip() for pf in players_fields]
    player_stats = {}
    for i in starters_index:
        for j in range(1,6):
            info = content[j+i]
            player_stats.update(buildPlayerStatsDict(players_fields,
                                                     info))
    for i,j in zip(bench_index, totals_index):
        for k in range(i+1,j):
            info = content[k]
            player_stats.update(buildPlayerStatsDict(players_fields,
                                                     info))
    return player_stats


def buildPlayerStatsDict(players_fields, info):
    name = info[0].split(',')[0].strip()
    pos = info[0].split(',')[1].strip()
    info = filter(empty_str_filter, info[1:])
    if len(info) < len(players_fields):
        stats_dict = {'notes': '<>'.join(info)}
    else:
        stats_dict = {field:value for\
                      field,value in zip(players_fields, info)}
    stats_dict['position'] = pos
    return {name : stats_dict}


def espnGameInfoFromBox(summary, game_id):
    """

    """
    details, content = headerAndContentFromBox(summary)
    game_info = {}
    game_info['game_id'] = game_id
    game_info['teams'] = teamsFromBox(details)
    game_info['stats'] = teamStatsFromBox(summary)
    game_info['starters'] = startersFromBox(details, content)
    game_info['bench'] = benchFromBox(details, content)
    return game_info


def teamsFromBox(details):
    start_index = startIndex(details)
    away = details[0][0]
    home = details[start_index[1]-1][0]
    return {'home':home, 'away':away}


def teamStatsFromBox(summary):
    details, content = headerAndContentFromBox(summary)
    totals_index = totalsIndex(details)
    totals_fields = filter(empty_str_filter,
                           details[totals_index[0]][1:])
    totals_fields = [tf.strip() for tf in totals_fields]
    totals = {}
    for i,n in zip(totals_index, ['away', 'home']):
         tot = filter(empty_str_filter, content[i+1])
         totals[n] = {field:value for\
                      field,value in zip(totals_fields, tot)}
    return totals
    

def startersFromBox(details, content):
    starters_index = startIndex(details)
    starters = {}
    for i,n in zip(starters_index, ['away', 'home']):
        s = []
        for j in range(1,6):
            name = content[j+i][0].split(',')[0].strip()
            s.append(name)
        starters[n] = s
    return starters


def benchFromBox(details, content):
    bench_index = benchIndex(details)
    totals_index = totalsIndex(details)
    bench = {}
    for i,j,n in zip(bench_index,
                     totals_index,
                     ['away', 'home']):
        b = []
        for k in range(i+1,j):
            name = content[k][0].split(',')[0].strip()
            b.append(name)
        bench[n] = b
    return bench


#////////////////////////////////////////////////////////////
#{ process the play-by-play nba page
#////////////////////////////////////////////////////////////


def espnPbpFromSoup(soup, labels):
    '''
    url is a play-by-play url obtained from score-summary ESPN page;
    use BeautifulSoup to parse apart data_in; all relevant data found
    in 'table' HTML structures, hence we grab those;
    '''
    tables = soup.find_all('div', {labels[0]:labels[1]})
    table = tables[1]
    pbp = table.findAll('tr')
    '''Use BS to get the headers (e.g., home and away team for game)'''
    header      = [str(h.text) for h in pbp[1].findAll('th')]
    content     = []
    for line in pbp[2:]:
        line = line.findAll('td')
        line = [str(e.text.encode('utf8')) for e in line]
        content.append(structurePbpContent(header, line))
    content = filter(None, content)
    return content


def structurePbpContent(head, line):
    """
    For a line in the play-by-play data, structure the raw info
    content into a dictionary.
    """
    try:
        line = {head[0]:line[0],
                head[1]:line[1] if len(line[1])>2 else '',
                head[2]:line[2],
                head[3]:line[3] if len(line[3])>2 else ''}
        
        return {'Event':'play',
                'Details':line}
    except IndexError:
        if len(line)==2:
            if 'timeout' in line[1].lower():
                line = {'Event':'timeout',
                        'Details':{'Time':line[0],
                                   'Text':line[1]}
                        }
            elif 'end' in line[1].lower():
                line = {'Event':'end_of_quarter',
                        'Details':{'Time':line[0],
                                   'Text':line[1]}
                        }
            else:
                line = {'Event':'other',
                        'Details': ';'.join(line)}
            return line
        else:
            return {}
    

#////////////////////////////////////////////////////////////
#{ process the game shots information
#////////////////////////////////////////////////////////////


def espnShotsFromSoup(soup, game_id):
    shots = soup.findAll('shot') #'Shot' or 'shot'?
    shot_dict = espnShotDictFromRaw(shots, game_id)
    return shot_dict


def espnShotDictFromRaw(shots, game_id):
    """
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
    """

    ShotDict = {}
    for s in shots:
        ShotDict[s['id']] = \
                          {'Q':s['qtr'],
                           'time' : s['d'].split(' ')[3],
                           'made' : '0' if s['made']=='false' else '1',
                           'pts' : '2' if s['d'].find('jumper')>-1 else '3',
                           'p' : s['p'],
                           'pid' : s['pid'],
                           't' : s['t'],
                           'x' : s['x'],
                           'y' : s['y'],
                           'game_id':game_id}
    return ShotDict
        
