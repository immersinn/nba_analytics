'''
Convert the pages pulled from ESPN by parseESPNPages into 'structured docs'
preps (i.e., dictionaries); failry straightforward

http://scores.espn.go.com/nba/boxscore?gameId=320223025
http://espn.go.com/nba/playbyplay?gameId=320223025&period=0
http://sports.espn.go.com/nba/gamepackage/data/shot?gameId=320223014
'''

import sys, os
import re
import parseESPNPages

pageTypeD = {'boxscore':'box',
             'playbyplay':'pbp',
             'shot':'shot'}


def structureESPNPage(url):
    ptype = re.search(r'//([a-z]+)/?',url)
    gameID = re.search(r'/?gameId=([0-9]{9})', url)
    try:
        ptype = pageTypeD[ptype.groups(0)[0]]
        gameID = gameID.groups(0)[0]
    except AttributeError:
        print "Unrecogonized URL; please provide a valid ESPN Page URL"
        raise
    '''Found the necessary info in the url; grab info from pages'''
    if ptype=='shot':
        pageDict = parseESPNPages.processESPNShotsPage(url)
    elif ptype=='playbyplay':
        data = parseESPNPages.processESPNpage(url, 'pbp')
        pageDict = page2dictPBP(data)
    elif ptype=='boxscore':
        data = parseESPNPages.processESPNpage(url, 'box')
        pageDict = page2dictBOX(data)
    '''Add Game ID to the page dictionary...'''
    pageDict['GameID'] = gameID
    return pageDict, ptype


def page2dictPBP(data):
    '''
    Play by Play page data:
    data['head']
    data['content']
    '''
    pageDict = dict()
    for i,line in enumerate(data):
        pageDict[i] = {head[0]:line[0],
                       head[1]:line[1] if len(line[1])>2 else '',
                       head[2]:line[2],
                       head[3]:line[3] if len(line[3])>2 else ''}
    return pageDict

def page2dictBOX(data):
    '''
    Boxscore page data:
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

def getUsedNames(player_ref):
    '''
    Get player names used in play-by-play data;
    Box_Score_Name : Play_by_Play_Name
    '''
    player_names = {}
    for entry in player_ref:
        entry = entry.split('\t')
        player_names[entry[0].replace('  ',' ')] =\
                    ' '.join(entry[1].split('/')[-1].split('-'))
    return player_names

def getESPNIDs(player_ref):
    '''
    Play_by_Play_Name : ESPN_ID
    '''
    player_IDs = {}
    for entry in player_ref:
        entry = entry.split('\t')
        player_IDs[' '.join(entry[1].split('/')[-1].split('-'))] =\
                       int(entry[1].split('/')[-2])
    return player_IDs

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

