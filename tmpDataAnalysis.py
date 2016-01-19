

import re


def shotsFromGames(games):
	shots = []
	for g in games:
		gshots = \
                       parseShotEntries(e.pbp.ix[e.pbp.EVENTMSGTYPE == 1,].copy())
		shots.extend(gshots)
	return(shots)


def parseShotEntries(pbp_df):
	shots = []
	for i in pbp_df.index:
		shots.append(parseShotEntry(pbp_df.ix[i,]))
	return(shots)


def parseShotEntry(event_line):
	if event_line.HOMEDESCRIPTION:
		d = event_line.HOMEDESCRIPTION
	elif event_line.VISITORDESCRIPTION:
		d = event_line.VISITORDESCRIPTION
	return({'descrip': d,
		'eventtype' : event_line.EVENTMSGTYPE,
		'eventsubtype' : event_line.EVENTMSGACTIONTYPE})


def knowShotMatch(shot_descrip):
    shot_dist_match = re.compile(r"[0-9]+'")
    shot_pt_match = re.compile(r"[2|3]PT")
    if re.search(shot_dist_match, shot_descrip):
        return(True)
    elif re.search(shot_pt_match, shot_descrip):
        return(True)
    else:
        return(False)


def main():
    with open('/home/immersinn/Data/DataDumps/NBA/pbpSubset02.pkl', 'r') as f1:
        pbp = pickle.load(f1)
    games = [nbaGame.GameEvents(p) for p in pbp]
    shots = shotsFromGames(games)
    unkn_shots = [s for s in shots if not knowShotMatch(s['descrip'])]
