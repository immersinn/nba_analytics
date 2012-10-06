'''
Messing with ESPN NBA Play-by-Play data
'''

with open('/Users/sinn/Desktop/NBA_TempGame_pbp.txt', 'r') as f1:
    pbp = f1.read()
pbp_lines = pbp.split('\n')
pbp_split = [line.split('\t') for line in pbp_lines]

pbp_quarters = pbp.split('Quarter Summary')
pbp_quarters_lines = [q.split('\n') for q in pbp_quarters]

# skip blank lines ['']
# skip ['xxx Quarter Summary']

mark = [line[0].find('Quarter Summary')>-1 or line==[''] for line in pbp_split]    


'''Need to get the starting linup for each team'''
with open('/Users/sinn/Desktop/NBA_TempGame_box_content.txt', 'r') as f1:
    box = f1.read().split('\n')
with open('/Users/sinn/Desktop/NBA_TempGame_box_details.txt', 'r') as f1:
    details = f1.read().split('\n')
with open('/Users/sinn/Desktop/NBA_TempGame_box_playerref.txt', 'r') as f1:
    player_ref = f1.read().split('\n')[1:-1]

# names in box score not nec. names used in pbp...
player_names = {}
for entry in player_ref:
    entry = entry.split('\t')
    player_names[entry[0].replace('  ',' ')] =\
                                    ' '.join(entry[1].split('/')[-1].split('-'))

start_index = [i for i in range(len(details)) if details[i].find('STARTERS')>-1]
team_1 = box[start_index[0]+1:start_index[0]+6]
team_1 = [entry.split(',')[0].replace('  ',' ') for entry in team_1]
team_1 = [player_names[name] for name in team_1]
# somehow a space gets added or removed here...
team_2 = box[start_index[1]:start_index[1]+5]
team_2 = [entry.split(',')[0].replace('  ',' ') for entry in team_2]
team_2 = [player_names[name] for name in team_2]


'''Locate substitutions by quarter'''
quarters_subs = {}
for i,q in enumerate(pbp_quarters_lines):
    quarters_subs[i+1] = \
                        [line for line in q if line.find('enters the game for')>-1]


'''
Get substitution players, times, scores.  Can't construct who's in the game
outside of the first quarter b/c not sure who's starting the quarter after
the 1st.  Need to reconstruct backwards...
'''
player_on_floor = []
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
        
        new_line['P_in']    = sub[0]
        new_line['P_out']   = sub[1]

        player_on_floor.append(old_line)
        old_line = new_line.copy()

    old_line['Time End'] = '0:00'
    score = pbp_quarters_lines[Q-1][-3].split('\t')[2] \
            if Q < 4 else pbp_quarters_lines[Q-1][-4].split('\t')[2]
    old_line['Score End'] = score
    player_on_floor.append(old_line)

    
