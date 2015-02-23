# prereq stuff
import sys, os
import pandas
import numpy
from collections import defaultdict

sys.path.append('/home/immersinn/Gits/Helper-Code/Python27')
import picklingIsEasy


"""
Step 01: Get shot information from shot pickled data
"""
sht_n = '/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/sht_20111215to20120622.pkl'
sht = picklingIsEasy.unpickledata(sht_n)

"""
Data in ShotDict (for current / future ref)
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
"""
max_x = 50
max_y = 47
AttemptedShots = dict()
MadeShots = dict()
players = set()
for game in sht.values():
    for shot in game['Shots'].values():
        if shot['p'] in players:
            AttemptedShots[shot['p']][shot['x'],shot['y']] += 1
            if shot['made']:
                MadeShots[shot['p']][shot['x'],shot['y']] += 1
        else:
            '''Create entry for player if not come across before'''
            players.add(shot['p'])
            AttemptedShots[shot['p']] = defaultdict(int)
            AttemptedShots[shot['p']][shot['x'],shot['y']] += 1
            MadeShots[shot['p']] = defaultdict(int)
            if shot['made']:
                MadeShots[shot['p']][shot['x'],shot['y']] += 1
n_players = len(players)       

"""
Step 02:  Create matricies from shot dictionaries
"""
# switch to sparse...
AttMat = numpy.zeros([max_x*max_y + 1, n_players],dtype=int)
MdeMat = numpy.zeros([max_x*max_y + 1, n_players],dtype=int)
p_index = dict()
for i,p in enumerate(AttemptedShots.keys()):
    p_index[i] = p
    for loc in AttemptedShots[p].keys():
        '''Rotate court here'''
        if int(loc[1]) in [-2,96]:   # foul shot
            row = max_x*max_y   # since row shifted down 1
        else:
            row = (int(loc[1])-1)*max_x + int(loc[0]) - 1 if int(loc[1]) <=47 \
                  else (94-int(loc[1])-1)*max_x + (50-int(loc[0])) - 1
        AttMat[row,i] = AttemptedShots[p][loc]
        MdeMat[row,i] = MadeShots[p][loc]

"""
Step 02b:
    Export the matrices as .csv for importing into R
    Use names as header
"""
p_index = [v.replace(u'\u0119',' ') for v in p_index.values()]
AttOut = ','.join(p_index) + '\n'
MdeOut = ','.join(p_index) + '\n'
for i in range(AttMat.shape[0]):
    AttOut += ','.join([str(n) for n in AttMat[i,]]) + '\n'
    MdeOut += ','.join([str(n) for n in MdeMat[i,]]) + '\n'

AttOut_name = '/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/shot_by_player_att_all.txt'
MdeOut_name = '/home/immersinn/Gits/NBA-Data-Stuff/DataFiles/shot_by_player_mde_all.txt'

with open(AttOut_name, 'w') as f1:
    f1.write(AttOut)
with open(MdeOut_name, 'w') as f1:
    f1.write(MdeOut)

print('fine')

#### Should prob do this in R ##
##"""
##Step 03a:  Cleaning
##"""
### something like less than N_shot shots in data...
##MdeMat_cl = MdeMat.copy()
##AttMat_cl = AttMat.copy()
##
##"""
##Step 03b:  Clustering
##"""
##
##'''Attempt 01: fraction of made shots from each location'''
##MdeShtFrac = numpy.divide(numpy.matrix(AttMat_cl,dtype=float),MdeAtt_cl) / \
##             MdeAtt_cl.sum(axis=0)
