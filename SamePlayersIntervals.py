'''
Takes the txt versions of the ESPN play-by-play data and constructs the
data for substitution intervals; players on court at the time, start time,
stop time, start score, stop score, substitution that occured; substitution
occurs at start of interval, if any;
each entry of track_subs =
{'Q':current qurter,
 'Time Start':initial time, 'Time End':final time (str),
 'Score Start':initial score, 'Score End':final score (str),
 'P_in':player substituted in, 'P_out':player subed out (str),
 'Players':players on the court at that time, including substitution
'''
import os, sys, re

def loadGameFilesTxt(basepath):
    '''
    Load the pbp (raw-ish) text file;
    Load other associated files (box, player names/refs)
    '''
    with open(os.path.join(basepath,'NBA_TempGame_pbp.txt'), 'r') as f1:
        pbp = f1.read()
    with open(os.path.join(basepath,'NBA_TempGame_box_content.txt'), 'r') as f1:
        box = f1.read().split('\n')
    with open(os.path.join(basepath,'NBA_TempGame_box_details.txt'), 'r') as f1:
        details = f1.read().split('\n')
    with open(os.path.join(basepath,'NBA_TempGame_box_playerref.txt'), 'r') as f1:
        player_ref = f1.read().split('\n')[1:-1]
    return pbp, box, details, player_ref

##def loadGameFilesDB():


def PBPsplitQuarters(pbp):
    '''Split by quarters'''
    pbp_quarters = pbp.split('Quarter Summary')
    pbp_quarters_lines = {}
    for i,entry in enumerate(pbp_quarters):
        pbp_quarters_lines[i+1] = entry.split('\n')
    return pbp_quarters_lines

def PBPsplitLines(pbp):
    '''Split by lines'''
    pbp_lines = pbp.split('\n')
    ##pbp_split = [line.split('\t') for line in pbp_lines]
    # skip blank lines ['']
    # skip ['xxx Quarter Summary']
    mark = [line[0].find('Quarter Summary')>-1 or line==[''] for line in pbp_split]
    return pbp_lines

def getUsedNames(player_ref):
    '''Get player names used in play-by-play data'''
    player_names = {}
    for entry in player_ref:
        entry = entry.split('\t')
        player_names[entry[0].replace('  ',' ')] =\
                    ' '.join(entry[1].split('/')[-1].split('-'))
    return player_names

def getESPNIDs(player_ref):
    player_IDs = {}
    for entry in player_ref:
        entry = entry.split('\t')
        player_IDs[' '.join(entry[1].split('/')[-1].split('-'))] =\
                       int(entry[1].split('/')[-2])
    return player_IDs

def getTeamPlayers(box, details, player_names):
    '''Determine all players for each team from the box score table'''
    start_index = [i for i in range(len(details)) if details[i].find('STARTERS')>-1]
    bench_index = [i for i in range(len(details)) if details[i].find('BENCH')>-1]
    total_index = [i for i in range(len(details)) if details[i].find('TOTALS')>-1]
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

def getSubTrack(pbp_quarters_lines, P, player_IDs):
    quarters_subs, quarters_subs_index = getSubIndex(pbp_quarters_lines)
    track_subs =\
               getInitialSubTrack(pbp_quarters_lines, quarters_subs)
    players_on_floor =\
                     getPlayersOnFloor(quarters_subs_index, pbp_quarters_lines, P)
    IPs = getInitialPlayers(track_subs, players_on_floor)
    track_subs = getFinalSubTrack(track_subs, IPs)
    track_subs = UpdateNames2IDs(track_subs, player_IDs)
    return track_subs

def getSubIndex(pbp_quarters_lines):
    '''Locate substitutions by quarter, get index of each line'''
    quarters_subs           = {}
    quarters_subs_index     = {}
    for i in pbp_quarters_lines.keys():
        q = pbp_quarters_lines[i]
        quarters_subs[i] = \
                            [line for line in q if line.find('enters the game for')>-1]
        quarters_subs_index[i] = \
                            [j for j in range(1,len(q)) \
                             if q[j].find('enters the game for')>-1]
    return quarters_subs, quarters_subs_index

def getInitialSubTrack(pbp_quarters_lines, quarters_subs):
    '''
    Get substitution players, times, scores.  Can't construct who's in the game
    outside of the first quarter b/c not sure who's starting the quarter after
    the 1st.  Need to reconstruct backwards using remainder of pbp data.
    '''
    track_subs = []
    default_line = {'Q':0,
                    'Time Start':0,'Time End':0,
                    'Score Start':0,'Score End':0}
    score = '0-0'
    for Q in quarters_subs.keys():
        old_line = default_line.copy()
        old_line['Q'] = Q
        old_line['Time Start'] = '12:00'
        old_line['Score Start'] = score
        for sub in quarters_subs[Q]:
            sub = sub.split('\t')
            time = sub[0]
            score = sub[2]
            if len(sub[1])==2:
                sub = sub[3].split('enters the game for')
                team = 2
            else:
                sub = sub[1].split('enters the game for')
                team = 1
                
            '''Update old line, new line'''
            new_line = old_line.copy()
            new_line['Team'] = team
            
            old_line['Time End'] = time
            new_line['Time Start'] = time

            old_line['Score End'] = score
            new_line['Score Start'] = score
            
            new_line['P_in']    = sub[0].lower().strip()
            new_line['P_out']   = sub[1].lower().strip()

            track_subs.append(old_line)
            old_line = new_line.copy()

        old_line['Time End'] = '0:00'
        score = pbp_quarters_lines[Q][-3].split('\t')[2] \
                if Q < 4 else pbp_quarters_lines[Q][-4].split('\t')[2]
        old_line['Score End'] = score
        track_subs.append(old_line)
    return track_subs

def getFinalSubTrack(track_subs, IPs):
    '''Update the "track subs" data to include the players on the floor at each time'''
    i = 0
    for Q in IPs.keys():
        players = list(IPs[Q])
        while i < len(track_subs) and track_subs[i]['Q']==Q:
            if 'P_in' in track_subs[i].keys():
                players[players.index(track_subs[i]['P_out'])] = track_subs[i]['P_in']
            track_subs[i]['Players'] = players[:]
            i += 1
    return track_subs

def UpdateNames2IDs(track_subs, player_IDs):
    '''Change all the player names to player IDs, via ESPN pages'''
    for i,line in enumerate(track_subs):
        track_subs[i]['Players'] = [player_IDs[p] for p in line['Players']]
        if 'P_in' in line.keys():
            track_subs[i]['P_in'] = player_IDs[line['P_in']]
            track_subs[i]['P_out'] = player_IDs[line['P_out']]
    return track_subs

def getPlayersOnFloor(quarters_subs_index, pbp_quarters_lines, P):
    '''Get set of players named during each sub-section of each quarter'''
    players_on_floor = []
    for Q in quarters_subs_index.keys():
        start_index = 0
        for sub_index in quarters_subs_index[Q]:
            players_on_floor.append(\
                {'Q': Q,
                 'Players':getPlayersInPlay(pbp_quarters_lines[Q][start_index:sub_index],P)})
            start_index = sub_index+1

        '''End-of-quarter update'''
        players_on_floor.append(\
            {'Q':Q,
             'Players':getPlayersInPlay(pbp_quarters_lines[Q][sub_index:],P)})
    return players_on_floor

def getPlayersInPlay(pbpLines, P):
    current_players = set()
    for line in pbpLines:
        new_players = getPlayersInLine(line,P)
        for p in new_players:
            current_players.add(p)
    return list(current_players)

def getPlayersInLine(pbpLine, P):
    players = list()
    pbpLine = pbpLine.split('\t')
    if len(pbpLine)==4:
        pbpLine = pbpLine[3] if len(pbpLine[1])==2 else pbpLine[1]
        player = matchPlayer(pbpLine,P)
        if player:
            players.append(player)
            pbpLine = re.search(r'\((.*)\)',pbpLine)
            if pbpLine:
                players.append(matchPlayer(pbpLine.groups()[0], P))
    return players

def matchPlayer(pbpLine, P):
    if ' '.join(pbpLine.split(' ')[:2]).lower() in P:
        player = ' '.join(pbpLine.split(' ')[:2]).lower()
    elif ' '.join(pbpLine.split(' ')[:3]).lower() in P:
        player = ' '.join(pbpLine.split(' ')[:3]).lower()
    else: player = ''
    return player
        

'''Determine which players start each Quarter'''
def getInitialPlayers(track_subs, players_on_floor):
    IPs = {}
    for Q in [1,2,3,4]:
        q_ts    = [line for line in track_subs if line['Q']==Q]
        q_pof   = [line for line in players_on_floor if line['Q']==Q]
        IPs[Q] = getQInitialPlayers(q_ts, q_pof)
    return IPs

def getQInitialPlayers(q_ts, q_pof):
    initial_players = set()
    subedin_players = set()
    i = 0
    while len(initial_players) != 10 and i < len(q_ts):
        # add subed in player to 'no fly' list
        # add subed out player to ip if not on 'no fly' list
        try:
            subedin_players.add(q_ts[i]['P_in'])
            if q_ts[i]['P_out'] not in subedin_players:
                initial_players.add(q_ts[i]['P_out'])
        except KeyError:
            pass
        # add found active players that have not been subed in
        for p in set(q_pof[i]['Players']).difference(subedin_players):
            initial_players.add(p)
        i += 1      # update line index
    if len(initial_players) != 10:
        print 'Warning!! All players not found!!!!!!!!!!1'
    return initial_players


'''
Put everything together to be run auto-magically; doesn't save anything yet,
just runs and displays sample of final result in terminal;
'''
if __name__=="__main__":
    basepath = '/Users/sinn/Desktop'
    '''Load game files'''
    pbp, box, details, player_ref = loadGameFilesTxt(basepath)
    '''Parse pbp'''
    pbp_quarters_lines = PBPsplitQuarters(pbp)
    '''Get player names for each team'''
    team_1, team_2 = getTeamPlayers(box, details, getUsedNames(player_ref))
    '''Construct the same-player-interval data'''
    track_subs = getSubTrack(pbp_quarters_lines, team_1+team_2, getESPNIDs(player_ref))
    for entry in track_subs[:10]: print entry
