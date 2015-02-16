
'''Load season stats for players file..'''
with open('/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/playerstats20120510040.txt', 'r') as f1:
    all_2011 = f1.read().split('\n')
all_2011 = [a.split('\t') for a in all_2011]
player_mins = [(' '.join(a[1].split(',')),a[3]) for a in all_2011 if a != ['']]
##mins = [float(p[1]) for p in player_mins[1:]]
pm_names = [p[0].lower().replace("'",'') for p in player_mins[1:]]
pm_names = [' '.join([' '.join(p.split('  ')[1:]),
                      p.split('  ')[0]]) for p in pm_names]
pm_set = set(pm_names)
'''Load 1st line from shots matrix file (i.e. player names)''' 
with open('/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/shot_by_player_att_all.txt','r') as f1:
    players = f1.readline().split(',')
players = [' '.join(p.lower().replace('jr.','').replace("'",'').strip().split('  ')).strip()\
           for p in players]
p_set = set(players)
'''Find index of matching player'''
indx = [players.index(p) if p in p_set else -1 for p in pm_names]
indxRev = [pm_names.index(p) if p in pm_set else -1 for p in players]

for n in p_set:
    if n not in pm_set:
	print(n)
for n in pm_set:
    if n not in p_set:
	print(n)
'''Hand replace some of the names, eh...'''
indx[pm_names.index('luc mbah a moute')] = players.index('luc richard mbah a moute')
indx[pm_names.index('louis amundson')] = players.index('lou amundson')
indx[pm_names.index('wes matthews')] = players.index('wesley matthews')
indx[pm_names.index('jose barea')] = players.index('jose juan barea')
indx[pm_names.index('nene hilario')] = players.index('nen')


indxRev[players.index('luc richard mbah a moute')] = pm_names.index('luc mbah a moute')
indxRev[players.index('lou amundson')] = pm_names.index('louis amundson')
indxRev[players.index('wesley matthews')] = pm_names.index('wes matthews')
indxRev[players.index('jose juan barea')] = pm_names.index('jose barea')
indxRev[players.index('nen')] = pm_names.index('nene hilario')

'''Create combo id-name-min file'''
with open('/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/playmins20112012.csv','w') as f1:
    f1.write(','.join(['Indx',player_mins[0][0],player_mins[0][1]])+'\n')
    for i,val in enumerate(indx):
	f1.write(','.join([str(val),player_mins[i+1][0],player_mins[i+1][1]]) + '\n')

with open('/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/indx.csv','w') as f1:
    f1.write(','.join([str(ii) for ii in indx]))

	
with open('/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/indxRev.csv','w') as f1:
    f1.write(','.join([str(ii) for ii in indxRev])
