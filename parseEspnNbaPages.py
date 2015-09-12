# -*- coding: utf-8 -*-
'''
Parsing modules specifically for handling ESPN sports pages (tested only on
NBA data thus far); grabs page @ url and gets pbp / box / extra (all?);
should be called by a function that is iterating over games for a particular
day, and push data to code that transmits it to a db
'''
import sys

sys.path.append('/Users/immersinn/Gits/')

from nba_analytics.webpage_parse.soupypages import checkBS4Type

null_value      = '&nbsp;'
empty_str_filter = lambda x: x not in ['', '\xc2\xa0']


#////////////////////////////////////////////////////////////
#{ process the recap / summary nba page from espn
#{ DOES NOT WORK PROPERLY AT THE MOMENT
#////////////////////////////////////////////////////////////


def espnRecapFromSoup(soup, attrs):
    """
    Really just the recaps page, but also will grab extra info here as well
    """
##    recap = pullContents(soup)
    recap = soup.getText(strip=True)
    return recap


def getText(raw):
    """Gets same summary text from recap page"""
    text_start = "<!-- begin recap text -->"    # these are super handy
    text_stops = "<!-- end recap text -->"
    text = raw[raw.find(text_start)+len(text_start):\
               raw.find(text_stops)]
    text = clean_html(text)
    return text

def pullContents(soup):
    try:
        header = soup.findAll('h2')[0].contents
    except IndexError:
        header = ''
    paras = soup.findAll('p')
    content = [cleanContents(p.contents) for p in paras]
    return {'header':header,
            'content':content}

def cleanContents(contents):
    temp = []
    for i in range(len(contents)):
	if checkBS4Type(contents[i], 'Tag'):
            if 'href' in contents[i].attrs.keys():
                temp.append(contents[i]['href'])
	elif checkBS4Type(contents[i], 'NavigableString'):
            temp.append(contents[i])
        else:
            temp.append('')
    return temp
    


#////////////////////////////////////////////////////////////
#{ process the box score nba page
#////////////////////////////////////////////////////////////


def espnBoxFromSoup(soup, labels, game_id):
    """
    :type soup: bs4 soup
    :param soup: soup form of box score ESPN page

    :type labels: list
    :param labels: specific html labels that correspond to important
    data in the box score table

    :type game_id: str
    :param game_id: ESPN game id for current game

    :rtype: dict

    Calls modules to extract desired info from ESPN box score page.
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
    """
    Splits the box score table into column header information
    ('details') and content rows (content).  Returns a tuple
    of these lists.
    """
    details     = []
    content     = []
    for line in summary:
        details.append([str(h.text.encode('utf8')) for h in line.findAll('th')])
        content.append([str(h.text.encode('utf8')) for h in line.findAll('td')])
    return details, content


def startIndex(details):
    """Determines lines where starter info begins"""
    start_index = [i for i in range(len(details)) if \
                   details[i] and details[i][0]=='STARTERS']
    return start_index


def benchIndex(details):
    """Determine lines where bench player info begins"""
    bench_index = [i for i in range(len(details)) if \
                   details[i] and details[i][0]=='BENCH']
    return bench_index


def totalsIndex(details):
    """Determines lines where team total info begins"""
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
    """
    Extracts information for the players in the game from the box
    score table.  This includes full names, ESPN player ids,
    and links to the players' ESPN pages. Returned as a dict object
    where player ESPN ids are the keys.
    """
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
    For each player listed in the box score, extracts the relevant
    game-summary stats for the player. Places in a dict object.

    Key: full player name recorded in box score table

    Value: dict, where each key is a stat attribute ('players_fields')
    and the value is the respective value recorded.

    Some players on the roster do not play.  Notes listed in the box
    score table are recorded for them in lieu of game stats.
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
    """
    :type players_fields: list
    :param players_fields: list of str stat names listed in the
    box score table

    :type info: str
    :param info: line from the box score table corresponding to
    a player in the game.  Contains summary stat info for player

    :rtype: dict

    Parses a line in the box score table corresponding to player
    data and structures into a dict object
    """
    name = info[0].split(',')[0].strip()
    try:
        pos = info[0].split(',')[1].strip()
    except IndexError:
        pos = 'N/A'
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
    :type summary: bs4 soup
    :param summary: table correspnding to box score data

    :type game_id: str
    :param game_id: ESPN id corresponding to game

    :rtype game_info: dict
    
    Calls methods to extract various data from the ESPN box score
    table and places into a dictionary
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
    """
    Determines the teams playing in the game from the box score data
    """
    start_index = startIndex(details)
    away = details[0][0]
    home = details[start_index[1]-1][0]
    return {'home':home, 'away':away}


def teamStatsFromBox(summary):
    """
    :type summary: bs4 soup
    :param summary: table correspnding to box score data

    :rtype totals: dict

    Parses the box score table and extracts game summary data for
    each team playing in the game.
    """
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
    """
    Extracts the names of the starting players for each team and
    returns a dict containing the home and away starters
    """
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
    """
    Extracts the non-starting plaeyers for each team and returns
    a dict containing the home and away players
    """
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
    """
    :type soup: bs4 soup
    :param soup: table from play-by-play ESPN page corresponding to
    the play-by-play data table

    :type labels: list
    :param labels: specific html labels that correspond to important
    data in the play-by-play table

    :rtype: list
    
    Parses the relevant table on the ESPN play-by-play page to extract
    each line item in the table.  Content is unstructured text data
    that still needs to be parsed to obtain information useful for
    analyzing the game flow.
    """
    tables = soup.find_all('div', {labels[0]:labels[1]})
    table = tables[1]
    pbp = table.findAll('tr')
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
    :type head: list
    :param head: column header info from play-by-play page

    :type line: str
    :param line: a single line from the play-by-play table

    :rtype: dict
    
    For a line in the play-by-play data, structure the raw info
    into a dict.

    Each key is a field indicated in "head". (away team name,
    score, home team name, time).  Field associated with a team
    name contains content if the event occuring on that line is
    associated with a player / players on that team.  Otherwise,
    empty string.

    Timeouts and end of quarter / game lines are also present and
    have a slightly different structure.

    Lines are denoted by their type ('Event' key in returnd
    dictionary; values are 'play', 'timeout', and 'end_of_quarter').
    Content from the line is recorded under the 'Details' key.
        
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
    """
    :type soup: bs4 soup
    :param soup: soup format of the ESPN shots xml file

    :type game_id: str
    :param game_id: ESPN game id for current game
    Extracts the shot data from the .xml file linked to
    the game.  Contains locations, shooter, missed/made,
    and pts.

    See "espnShotDictFromRaw" for details.
    """
    shots = soup.findAll('shot') #'Shot' or 'shot'?
    shot_info_dict = espnShotDictFromRaw(shots, game_id)
    shot_info_list = shotsDictToList(shot_info_dict)
    return shot_info_list


def shotsDictToList(shot_info_dict):
    """
    Converts shot
    """
    shot_info_list = []
    for k,v in shot_info_dict.items():
        v['shot_id'] = k
        shot_info_list.append(v)
    return shot_info_list


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

    Free-throws are not included in shot diagram, but are included
    in play-by-play
    """

    ShotDict = {}
    for s in shots:
        if s['d'].find('jumper')>-1:
            pts = 2
        elif s['d'].find('3-pointer')>-1:
            pts = 3
        else:
            pts = 0
        ShotDict[s['id']] = \
                          {'Q':s['qtr'],
                           'time' : s['d'].split(' ')[3],
                           'made' : 0 if s['made']=='false' else 1,
                           'pts' : pts,
                           'p' : s['p'],
                           'pid' : s['pid'],
                           't' : s['t'],
                           'x' : int(s['x']),
                           'y' : int(s['y']),
                           'game_id':game_id}
    return ShotDict
        
