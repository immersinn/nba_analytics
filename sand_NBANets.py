import re


"""
Quick get names in pbp
"""
ex_pbp.pop('GameID')
t1 = [t['WASHINGTON'].split(' ')\
      for t in ex_pbp.values() if 'WASHINGTON' in t.keys()]
t2 = [t['PHILADELPHIA'].split(' ')\
      for t in ex_pbp.values() if 'PHILADELPHIA' in t.keys()]

def namesOnly(plays):
    '''Get all words, except Jumpball, that begin w/ caps'''
    for j,t in enumerate(plays):
	v = list()
	for i in t:
            if i and i not in ['Jumpball:']:
                if re.match('[A-Z]',i[0]):
                    v.append(i)
	plays[j] = v
    return plays
                    
def getNames(NOs):
    '''Just assumes adjacent cap'd words are names; MWP f's this up'''
    names = set()
    for e in NOs:
	while len(e)>1:
	    names.add(' '.join(e[:2]))
	    e = e[2:]
    names = set([n for n in names if not n.endswith("'s")])
    return names

"""
Just get connections somehow
"""
##for line in plays:
##    if line[team01]:
##        pass
##    elif line[team02]:
##        pass
##    else:
##        #play break
##        pass
                    

def cleanLine(pbpL):
    pbpL = re.sub('\(|\)',' ', pbpL).split(' ')             # rmv (),split
    caps = [len(re.findall('[A-Z]',i)) > 0 for i in pbpL]     # cap'd words
    nnn = []                                                # names occ in line
    t = ''
    for i,val in enumerate(caps):
	if val:
	    t += ' ' + pbpL[i]
	else:
	    if len(t)>0: nnn.append(t.strip())
	    t = ''
