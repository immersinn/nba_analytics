'''
Convert the pages pulled from ESPN by parseESPNPages into 'structured docs'
preps (i.e., dictionaries); fairly straightforward

http://scores.espn.go.com/nba/boxscore?gameId=320223025
http://espn.go.com/nba/playbyplay?gameId=320223025&period=0
http://sports.espn.go.com/nba/gamepackage/data/shot?gameId=320223014
'''

import sys, os
import re
import parseESPNPages


def structureESPNPage(url):
    """
    Takes an input url, determine which type of page it is (or isn't),
    calls parseESPNPages to get the data from the page, and converts
    data intoa  dictionary for returning to the call.
    """
    gameID = re.search(r'\?gameId=([0-9]{9})', url)
    gameID = gameID.groups(0)[0]
    '''Find the necessary info in the url; grab info from pages'''
    if 'playbyplay' in url:
        data = parseESPNPages.processESPNPage(url, 'pbp')
        pageDict = {'Plays':page2dictPBP(data)}
        ptype = 'pbp'
    elif 'boxscore' in url:
        data = parseESPNPages.processESPNPage(url, 'box')
        pageDict = data
        #pageDict = page2dictBOX(data)
        ptype = 'box'
    elif 'shot' in url:
        pageDict = {'Shots':parseESPNPages.processESPNShotsPage(url)}
        ptype = 'shot'
    else:
        print "Unrecogonized URL; please provide a valid ESPN Page URL"
    '''Add Game ID to the page dictionary...'''
    pageDict['GameID'] = gameID
    return pageDict

def page2dictPBP(data):
    '''
    Takes play-by-play data from parseESPNPages and converts to
    a list of dictionary objects. Some ESPN pages have been known
    to have plays out of order, etc., hence the list structure.
    
    Play by Play page data structure from parseESPNPages:
    data['head']
    data['content']
    '''
    pageDict = dict()
    head = data['head']
    for i,line in enumerate(data['content']):
        # mongodb only takes strings as keys (bit of a pain),
        # so switching this over to str num keys, not ints (04/12/12)
        try:
            pageDict[str(i)] = {head[0]:line[0],
                           head[1]:line[1] if len(line[1])>2 else '',
                           head[2]:line[2],
                           head[3]:line[3] if len(line[3])>2 else ''}
        except:
            if len(line)==2:
                if 'timeout' in line[1].lower():
                    pageDict[i] = {'Time':line[0],
                                   'Timeout':line[1]}
                elif 'end' in line[1].lower():
                    pageDict[i] = {'Time':line[0],
                                   'EndOf':line[1]}
                else:
                    pageDict[i] = {'Other': ';'.join(line)}
    return pageDict

def page2dictBOX(data):
    '''
    Box score output from parseESPNPages to (loose) dictionary.  Not
    too much processing here, as the only real reasons to vist the box
    score page are to
    i) Get the player names used in the pbp data
    ii) Get the urls for each player
    iii) Obtain data for confirming any pbp parsing in the future (i.e,
    does the calculated rbs from player xxxx match the box score?)
    iv) Obtain the list of starters for the game, so that the
    "Who is on the court?" code can be verified.
    
    Boxscore page data from parseESPNPages:
    data['details']
    data['content']
    data['playerlinks']
    '''
    pageDict = dict()

    player_names = getUsedNames(data['playerlinks'])
    player_ids = getESPNIDs(data['playerlinks'])
    box_data = BoxInfo(box, details, player_names, player_ids)
    teamsheader = TeamsHeader(data['details'])
    boxinfo = BoxInfo(box, details, player_names, player_ids)

    '''Put home / away team and the stats header in the pageDict'''
    pageDict['header'] = teamsheader['header']
    pageDict['home'] = teamsheader['home']
    pageDict['away'] = teamsheader['away']
    '''Define starters, bench for home, away'''
    pageDict['StartersHome']    = "|".join(boxinfo['team_2'][:5])
    pageDict['BenchHome']       = "|".join(boxinfo['team_2'][5:])
    pageDict['StartersAway']    = "|".join(boxinfo['team_1'][:5])
    pageDict['BenchAway']       = "|".join(boxinfo['team_1'][5:])
    '''Set up player_name : player_id pairs'''
    for key in player_ids.keys():
        pageDict[key] = player_ids[key]
    '''Put info from boxinfo into pageDict; double-up on team_1, team_2'''
    for key in boxinfo.keys():
        pageDict[key] = boxinfo[key]
    return pageDict


def BoxInfo(box, details, player_names, player_ids):
    '''
    Helper function for 'page2dictBOX'; visits each component,
    does useful stuff for organizing, etc.
    '''
    boxdata = dict()
    '''Index of each important break in the data'''
    start_index = [i for i in range(len(details)) if details[i].find('STARTERS')>-1]
    bench_index = [i for i in range(len(details)) if details[i].find('BENCH')>-1]
    total_index = [i for i in range(len(details)) if details[i].find('TOTALS')>-1]
    '''Get players on each team'''
    boxdata['team_1'], boxdata['team_2'] = getTeamPlayers(box,
                                                          start_index,
                                                          bench_index,
                                                          total_index,
                                                          player_names)
    '''Get player box scores stats, team stats, teams, header'''
    playerdetails = getPlayerDetails(box, player_names, player_ids)
    extrasdetails = getExtrasDetails(box, start_index, total_index)
    for key in playerdetails.keys():
        boxdata[key] = playerdetails[key]
    for key in extrasdetails.keys():
        boxdata[key] = extrasdetails[key]
    return boxdata


def getTeamPlayers(box, start_index, bench_index, total_index, player_names):
    '''Determine all players for each team from the box score table'''
    team_1 = box[start_index[0]+1:start_index[0]+6]
    team_1.extend(box[bench_index[0]+1:total_index[0]])
    team_1 = [entry.split(',')[0].replace('  ',' ') for entry in team_1]
    team_1 = [player_names[name] for name in team_1]
    # somehow a space gets added or removed here...
    team_2 = box[start_index[1]:start_index[1]+5]
    team_2.extend(box[bench_index[1]:total_index[1]-1])
    team_2 = [entry.split(',')[0].replace('  ',' ') for entry in team_2]
    team_2 = [player_names[name] for name in team_2]
    return team_1, team_2

def getPlayerDetails(box, player_names, player_ids):
    '''
    Grabs box score details for each player;
    ESPN_ID : Box_Score_Line
    '''
    playerdetails = dict()
    for line in box:
        if line.split(',')[0].replace('  ',' ') in player_names.keys():
            playerdetails[player_ids[player_names[line.split(',')[0].replace('  ',' ')]]] = \
                                                                               line.split(',')[1]
    return playerdetails

def getExtrasDetails(box, start_index, total_index):
    '''
    Grabs all the extra stuff sitting after the team totals and such;
    accounts for extra space in details data stuff;
    '''
    extrasdetails = dict()
    extrasdetails['homeExtra'] = box[total_index[0]:start_index[1]]
    extrasdetails['awayExtra'] = box[total_index[1]-1:]
    return extrasdetails

def TeamsHeader(details, start_index):
    '''Grabs home / away team and stats header'''
    teamsheader = dict()
    teamsheader['away'] = details[0]
    teamsheader['home'] = details[start_index[1]-2]
    teamsheader['header'] = '\t'.join(details[start_index[0]-1].split('\t')[1:])
    return teamsheader

