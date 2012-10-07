'''
Messing with ESPN NBA Play-by-Play data...
'''


'''
Load the pbp (raw-ish) text file;
Load other associated files (box, player names/refs)
'''
with open('/Users/sinn/Desktop/NBA_TempGame_pbp.txt', 'r') as f1:
    pbp = f1.read()
with open('/Users/sinn/Desktop/NBA_TempGame_box_content.txt', 'r') as f1:
    box = f1.read().split('\n')
with open('/Users/sinn/Desktop/NBA_TempGame_box_details.txt', 'r') as f1:
    details = f1.read().split('\n')
with open('/Users/sinn/Desktop/NBA_TempGame_box_playerref.txt', 'r') as f1:
    player_ref = f1.read().split('\n')[1:-1]
    

'''Split by lines'''
pbp_lines = pbp.split('\n')
pbp_split = [line.split('\t') for line in pbp_lines]
# skip blank lines ['']
# skip ['xxx Quarter Summary']
mark = [line[0].find('Quarter Summary')>-1 or line==[''] for line in pbp_split]


'''Split by quarters'''
pbp_quarters = pbp.split('Quarter Summary')
pbp_quarters_lines = {}
for i,entry in enumerate(pbp_quarters):
    pbp_quarters_lines[i+1] = entry.split('\n')


'''Get player names used in play-by-play data'''
player_names = {}
for entry in player_ref:
    entry = entry.split('\t')
    player_names[entry[0].replace('  ',' ')] =\
                ' '.join(entry[1].split('/')[-1].split('-'))


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


'''Get set of players named during each sub-section of each quarter'''
players_on_floor = []
for Q in quarters_subs_index.keys():
    start_index = 0
    for sub_index in quarters_subs_index[Q]:
        players_on_floor.append(\
            {'Q': Q,
             'Players':getPlayersInPlay(pbp_quarters_lines[Q][start_index:sub_index])})
        start_index = sub_index+1

    '''End-of-quarter update'''
    players_on_floor.append(\
        {'Q':Q,
         'Players':getPlayersInPlay(pbp_quarters_lines[Q][sub_index:])})


def getPlayersInPlay(pbpLines):
    current_players = set()
    for line in pbpLines:
        new_players = getPlayersInLine(line)
        for p in new_players:
            current_players.add(p)
    return list(current_players)

def getPlayersInLine(pbpLine):
    players = list()
    pbpLine = pbpLine.split('\t')
    if len(pbpLine)==4:
        pbpLine = pbpLine[3] if len(pbpLine[1])==2 else pbpLine[1]
        if ' '.join(pbpLine.split(' ')[:2]).lower() in team_1+team_2:
            players.extend([' '.join(pbpLine.split(' ')[:2]).lower()])
            pbpLine = re.search(r'\((.*)\)',pbpLine)
            if pbpLine:
                players.extend([' '.join(pbpLine.groups()[0].split(' ')[:2]).lower()])
    return(players)
        
        
'''Get which players start each Quarter'''
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
        # add found active players that have not been subed in
        for p in set(q_pof[i]['Players']).difference(subedin_players):
            initial_players.add(p)
        # add subed in player to 'no fly' list
        # add subed out player to ip if not on 'no fly' list
        try:
            subedin_players.add(q_ts[i]['P_in'])
            if q_ts[i]['P_out'] not in subedin_players:
                initial_players.add(q_ts[i]['P_out'])
        except KeyError:
            pass
        i += 1      # update line index  
    return initial_players


