# -*- coding: utf-8 -*-
import sys, os
sys.path.append('/Users/sinn/NBA-Data-Stuff')
import prepworkURL

gameID = '320223014'
end = '00000'       # don't actually need this, I don't think..

shotURL = "http://sports.espn.go.com/nba/gamepackage/data/shot?gameId=320223014&end=32022301400000"
shotURL_mod = "http://sports.espn.go.com/nba/gamepackage/data/shot?gameId=320223014"

shotSoup = prepworkURL.makeSoup(prepworkURL.makePage(shotURL_mod),
                                shotURL_mod)
shots = shotSoup.findAll('Shot')

'''
Components of the shot:
d       --> pbp-esq discription (Made 19ft jumper 11:44 in 1st Qtr."
id      --> the shot id (gameID+xxxxx)
made    --> T/F
p       --> player shooting (same as pbp name)
pid     --> player ID (super usefull)
qtr     --> quarter (what does OT look like??)
t       --> ?? values: a, h,
x       --> x-cord where shot was taken from
y       --> y-cord where shot was taken from

I'm assuming this holds (from basketballgeek.com/data)
How do I interpret the (x,y) shot location coordinates?:
If you are standing behind the offensive team’s hoop then
the X axis runs from left to right and the Y axis runs from
bottom to top. The center of the hoop is located at (25, 5.25).
x=25 y=-2 and x=25 y=96 are free-throws (8ft jumpers)
'''

'''Transform into a dictionary; worry about matching up to pbp later...'''
ShotDict = {}
for s in shots:
    ShotDict[s['id']] = \
                      {'Q':s['qtr'],
                       'time' : s['d'].split(' ')[3],
                       'made' : u'0' if s['made']=='false' else u'1',
                       'pts' : u'2' if s['d'].find('jumper')>-1 else u'3',
                       'p' : s['p'],
                       't' : s['t'],
                       'x' : s['x'],
                       'y' : s['y']}
