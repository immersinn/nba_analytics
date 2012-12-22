# prereq stuff
import sys, os
import pandas
import numpy as py
import scipy.stats as stats
from collections import defaultdict

sys.path.append('/home/immersinn/Gits/Helper-Code/Python27')
import picklingIsEasy


"""
Step 01: Get shot information from shot pickled data
"""
sht_n = '/home/immersinn/Gits/NBA-Data-Stuff/sht_20111215to20111221.pkl'
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
    for shot in game.values()['Shots']:
        if shot['p'] in players:
            AttemptedShots[shot['p']][shot['x'],shot['y']] += 1
            if shot['made']:
                MadeShots[shot['p']][shot['x'],shot['y']] += 1
        else:
            '''Create entry for player if not come across before'''
            players.add(shot[p])
            AttemptedShots[shot['p']] = defaultdict(int)
            AttemptedShots[shot['p']][shot['x'],shot['y']] += 1
            MadeShots[shot['p']] = defaultdict(int)
            if shot['made']:
                MadeShots[shot['p']][shot['x'],shot['y']] += 1
        

"""
Step 02:  Create matricies from shot dictionaries
"""
# switch to sparse...
AttMat = numpy.zeros([max_x*max_y, n_players],dtype=int)
MdeMat = numpy.zeros([max_x*max_y, n_players],dtype=int)
p_index = dict()
for i,p in enumerate(AttemptedShots.keys()):
    p_index[i] = p
    for loc in AttemptedShots[player].keys():
        '''Rotate court here'''
        row = (loc[1]-1)*max_x + loc[0] if loc[1] <=47 \
              else (94-loc[1]-1)*max_x + (50-loc[0])
        AttMat[row,i] = AttemptedShots[player]
        MdeMat[row,i] = MadeShots[player]

"""
Step 02b:
    Export the matrices as .csv for importing into R
    Use names as header
"""
AttOut = ','.join(p_index.values()) + '\n'
MdeOut = ','.join(p_index.values()) + '\n'
for i in AttMat.shape()[0]:
    AttOut += ','.join([str(n) for n in AttMat[i,]])
    MdeOut += ','.join([str(n) for n in MdeMat[i,]])

with open(AttOut_name, 'w') as f1:
    f1.write(AttOut)
with open(MdeOut_name, 'w') as f1:
    f1.write(MdeOut)



## Should prob do this in R ##
"""
Step 03a:  Cleaning
"""
# something like less than N_shot shots in data...
MdeMat_cl = MdeMat.copy()
AttMat_cl = AttMat.copy()

"""
Step 03b:  Clustering
"""

'''Attempt 01: fraction of made shots from each location'''
MdeShtFrac = numpy.divide(numpy.matrix(AttMat_cl,dtype=float),MdeAtt_cl) / \
             MdeAtt_cl.sum(axis=0)
