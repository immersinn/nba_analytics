

import re
import pandas


####################################################
### PBP Preprocess
####################################################

HEADER = ["GAME_ID",
          "EVENTNUM",
          "EVENTMSGTYPE",
          "EVENTMSGACTIONTYPE",
          "PERIOD",
          "WCTIMESTRING",
          "PCTIMESTRING",
          "HOMEDESCRIPTION",
          "NEUTRALDESCRIPTION",
          "VISITORDESCRIPTION",
          "SCORE",
          "SCOREMARGIN"]


def preprocessPbp(pbp):
    pbp = pbpDict2Df(pbp)
    pbp = addGameClock(pbp)
    return(pbp)


def pbpDict2Df(pbp):
    # Build the play-by-play DataFrame from the pbp dictionary
    p_ord = []
    if 'play_by_play' in pbp.keys():
        for i in sorted([int(k) for k in pbp['play_by_play'].keys()]):
                p_ord.append(pbp['play_by_play'][str(i)])
    else:
        for i in sorted([int(k) for k in pbp.keys()]):
                p_ord.append(pbp[str(i)])
    pbp = pandas.DataFrame(p_ord,
                           columns=HEADER)
    
    return(pbp)


def addIndex(pbp):
    ind = pandas.DataFrame(data = range(pbp.shape[0]),
                           columns = ['Index'])
    pbp = pbp.join(ind)
    return(pbp)


def addGameClock(pbp):
    gc = [time2Gc(t) for t in pbp.PCTIMESTRING]
    gc = pandas.DataFrame(data = gc,
                          columns = ['GAMECLOCK'])
    pbp = pbp.join(gc)
    return(pbp)


def time2Gc(time):
    gc = 60 * int(time.split(':')[0]) + int(time.split(':')[1])
    return(gc)


####################################################
### Player Names in PBP
####################################################


def determinePlayerPBPNames(players, pbp_df):
    new_players = []
    for team in ['home', 'away']:
        sub_players = [p for p in players if p['hORa']==team]
        sub_pbp_descrip = pbp_df.HOMEDESCRIPTION if team=='home' \
                          else pbp_df.VISITORDESCRIPTION
        sub_pbp_names = getNamesUsedPBP(sub_pbp_descrip)
        new_players.extend(matchPlayers2PBPNames(sub_players,
                                                 sub_pbp_names))
    return(new_players)


def getNamesUsedPBP(pbp_descrip, method = 'sub'):
    names = []
    for d in pbp_descrip:
        if d:
            nd = d.split()
            d = []
            i = 0
            while i < len(nd):
                w = nd[i]
                if w[-1] == '.':
                    w += ' ' + nd[i+1]
                    i += 1
                d.append(w)
                i += 1
            names = findNameInLine(names, d, method)
    names = set(names)
    return(names)


def findNameInLine(names, d, method):
    if method == 'sub':
        if d[0] == 'SUB:':
            for_loc = d.index('FOR')
            names.append(' '.join(d[1:for_loc]))
            names.append(' '.join(d[for_loc+1:]))
    elif method == 'all':
        if d[0] == 'MISS':
            names.append(d[1])
        elif d[1] == 'REBOUND':
            names.append(d[0])
        elif d[2] == 'REBOUND':
            names.append(' '.join(d[:2]))
        elif d[-1] == 'PTS)':
            names.append(d[0])
        elif d[-1] == 'AST)':
            names.append(d[-3][1:])
            names.append(d[0])
    return(names)


def matchPlayers2PBPNames(players, pbp_names):

    for v in players:
	n = v['name']
	n = n.split()
	v['last_name'] = n[-1]
	v['first_init'] = n[0][0]
	v['middle_init'] = n[1][0] if len(n)>2 else ''
	v['middle_name'] = n[1] if len(n)>2 else ''

    for p in players:
        if p['middle_name'] and p['middle_name'] + ' ' + p['last_name'] in pbp_names:
            p['pbp_name'] = p['middle_name'] + ' ' + p['last_name']
        elif p['first_init'] + '. ' + p['last_name'] in pbp_names:
            p['pbp_name'] = p['first_init'] + '. ' + p['last_name']
        elif p['first_init'] + '.' + p['last_name'] in pbp_names:
            p['pbp_name'] = p['first_init'] + '.' + p['last_name']
        elif p['last_name'] in pbp_names:
            p['pbp_name'] = p['last_name']
        else:
            p['pbp_name'] = ''

    return(players)


####################################################
### Create individual Events from pbp
####################################################

# iterate over events
    # if event contains multiple single entries --> split
    # for each entry, determine player involved


def detEventType(event_line):
    """
    event message types and select action types:

    1 --> shot made
    2 --> shot missed
    3 --> free throw make and miss
        10 --> Single foul shot
        11 --> 1 of 2
        12 --> 2 of 2
    4 --> rebound
        0 --> Individual Rebound
        1 --> Team Rebound
    5 --> turnover
        1 --> bad pass + steal
        2 --> lost ball + steal
        3 -->
        4 --> traveling
        5 --> foul turnover
        11 --> shot clock
    6 --> Foul
        1 --> Personal Foul ("P.FOUL")
        2 --> Shooting Foul ("S.FOUL")
        3 --> L.B.FOUL
        4 --> Offensive foul ("OFF.FOUL")
        26 --> Offensive Charge Foul
        28 --> Personal Take Foul
    7 --> Violation
        2 --> Defensive Goaltending
        5 --> Kicked Ball
    8 --> Substitution
    9 --> Timeout
    10 --> jump ball
    11 --> ???
    12 --> quarter start
    13 --> quarter end / game end
    """
    
    if event_line.EVENTMSGTYPE == 1:
        state = 'MadeShot'
    elif event_line.EVENTMSGTYPE == 2:
        state = 'MissShot'
    elif event_line.EVENTMSGTYPE == 3:
        state = 'FreeThrow'
    elif event_line.EVENTMSGTYPE == 4:
        state = 'Rebound'
    elif event_line.EVENTMSGTYPE == 5:
        state = 'Turnover'
    elif event_line.EVENTMSGTYPE == 6:
        state = 'Foul'
    elif event_line.EVENTMSGTYPE == 7:
        state = 'Violation'
    elif event_line.EVENTMSGTYPE == 8:
        state = 'Sub'
    elif event_line.EVENTMSGTYPE == 9:
        state = 'Timeout'
    elif event_line.EVENTMSGTYPE == 10:
        state = 'JumpBall'
    elif event_line.EVENTMSGTYPE == 11:
        state = 'UKWN'
    elif event_line.EVENTMSGTYPE == 12:
        state = 'QuarterStart'
    elif event_line.EVENTMSGTYPE == 13:
        state = 'QuarterEnd'
    else:
        state = event_line.EVENTMSGTYPE
    return(state)



def events2Entries(pbp_df):
    entries = []
    for i in pbp_df.index:
        entries.extend(event2Entry(pbp_df.ix[i,]))
    return(entries)


def event2Entry(event_line):
    if event_line.EVENTMSGTYPE == 1:
        entries = splitShot(event_line)
    elif event_line.EVENTMSGTYPE == 2:
        entries = splitMiss(event_line)
    elif event_line.EVENTMSGTYPE == 5:
        entries = splitTurnover(event_line)
    elif event_line.EVENTMSGTYPE == 8:
        entries = splitSub(event_line)
    elif event_line.EVENTMSGTYPE == 10:
        entries = splitJumpBall(event_line)
    else:
        entries = basicEventPreProc(event_line)
    return(entries)


def basicEventPreProc(event_line):
    entries = []
    p1_team, d1 = descripsAndTeams(event_line)
    if event_line.EVENTMSGTYPE == 3:
        e1_name = 'FOULSHOT'
        p1_name = playerFromShot(event_line, p1_team)
    elif event_line.EVENTMSGTYPE == 4:
        e1_name = 'REBOUND'
        t1 = 'rebound'
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
    elif event_line.EVENTMSGTYPE == 6:
        e1_name = 'FOUL'
        t1 = foulTypePhrase(event_line)
        if t1:
            p1_name = playerFromTOBegin(event_line, p1_team, t1)
        else:
            # OK, attempted catch-all
            # way too many types; kick out to GameEvents level to fix
            e1_name = 'FOUL-UNKN'
            p1_name = 'unknown'
    elif event_line.EVENTMSGTYPE == 7:
        e1_name = 'VIOLATION'
        t1 = 'violation:'
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
    elif event_line.EVENTMSGTYPE == 9:
        e1_name = 'TIMEOUT'
        t1 = 'timeout:'
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
    elif event_line.EVENTMSGTYPE == 11:
        e1_name = 'UKWN'
        p1_name = 'GameEvent'
    elif event_line.EVENTMSGTYPE == 12:
        e1_name = 'QUARTERSTART'
        p1_name = 'GameEvent'
    elif event_line.EVENTMSGTYPE == 13:
        e1_name = 'QUARTEREND'
        p1_name = 'GameEvent'
    else:
        e1_name = None
        p1_name = None

    if p1_name:
        entries.append({'Event' : e1_name,
                        'Player' : p1_name,
                        'Team' : p1_team,
                        'DESCRIPTION' : d1,
                        'EVENTNUM' : int(event_line.EVENTNUM),
                        'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                        'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                        'PERIOD' : int(event_line.PERIOD),
                        'GAMECLOCK' : int(event_line.GAMECLOCK),
                        })
    return(entries)
    

def splitShot(event_line):
    entries = []
    p1_team, d = descripsAndTeams(event_line)
    p2_team = p1_team
    p1_name = playerFromShot(event_line, p1_team)
    if p1_name:
        e1_name = 'SHOT'; d1 = d;
        entries.append({'Event' : e1_name,
                        'Player' : p1_name,
                        'Team' : p1_team,
                        'DESCRIPTION' : d1,
                        'EVENTNUM' : int(event_line.EVENTNUM),
                        'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                        'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                        'PERIOD' : int(event_line.PERIOD),
                        'GAMECLOCK' : int(event_line.GAMECLOCK),
                        })
    p2_name = playerFromAst(event_line, p2_team)
    if p2_name:
        e2_name = 'ASSIST'; d2 = d;
        entries.append({'Event' : e2_name,
                        'Player' : p2_name,
                        'Team' : p2_team,
                        'DESCRIPTION' : d2,
                        'EVENTNUM' : int(event_line.EVENTNUM),
                        'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                        'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                        'PERIOD' : int(event_line.PERIOD),
                        'GAMECLOCK' : int(event_line.GAMECLOCK),
                        })
    return(entries)


def splitMiss(event_line):
    entries = []
    p1_team, d1, p2_team, d2 = descripsAndTeams(event_line,
                                                t1 = 'miss',
                                                num_players = 2)
    p1_name = playerFromShot(event_line, p1_team)
    e1_name = 'MISS'
    if d2:
        p2_name = playerFromTOBegin(event_line,
                                    p2_team,
                                    'block')
        e2_name = 'BLOCK'
    else:
        p2_name = None

    if p1_name:
        entries.append({'Event' : e1_name,
                        'Player' : p1_name,
                        'Team' : p1_team,
                        'DESCRIPTION' : d1,
                        'EVENTNUM' : int(event_line.EVENTNUM),
                        'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                        'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                        'PERIOD' : int(event_line.PERIOD),
                        'GAMECLOCK' : int(event_line.GAMECLOCK),
                        })
    if p2_name:
        entries.append({'Event' : e2_name,
                        'Player' : p2_name,
                        'Team' : p2_team,
                        'DESCRIPTION' : d2,
                        'EVENTNUM' : int(event_line.EVENTNUM),
                        'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                        'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                        'PERIOD' : int(event_line.PERIOD),
                        'GAMECLOCK' : int(event_line.GAMECLOCK),
                        })
    return(entries)


def splitTurnover(event_line):
    """
    1 --> bad pass + steal
    2 --> lost ball + steal
    3 -->
    4 --> traveling
    5 --> foul turnover
    11 --> shot clock
    """
    entries = []
    if event_line.EVENTMSGACTIONTYPE == 1:
        t1 = 'bad pass'; t2 = 'steal'
        p1_team, d1, p2_team, d2 = descripsAndTeams(event_line,
                                                    t1,
                                                    num_players = 2)
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
        e1_name = 'BADPASS'
        if d2:
            p2_name = playerFromTOBegin(event_line, p2_team, t2)
            e2_name = 'STEAL'
        else:
            p2_name = None
    elif event_line.EVENTMSGACTIONTYPE == 2:
        t1 = 'lost ball'; t2 = 'steal'
        p1_team, d1, p2_team, d2 = descripsAndTeams(event_line,
                                                    t1,
                                                    num_players = 2)
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
        e1_name = 'LOSTBALL'
        if d2:
            p2_name = playerFromTOBegin(event_line, p2_team, t2)
            e2_name = 'STEAL'
        else:
            p2_name = None
##    elif event_line.EVENTMSGACTIONTYPE == 3:
##        p1_name  = None; p2_name = None;
    elif event_line.EVENTMSGACTIONTYPE == 4:
        t1 = 'traveling'
        p1_team, d1 = descripsAndTeams(event_line)
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
        e1_name = 'TRAVELING'
        p2_name = None
    elif event_line.EVENTMSGACTIONTYPE == 5:
        t1 = 'foul'
        p1_team, d1 = descripsAndTeams(event_line)
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
        e1_name = 'FOUL'
        p2_name = None
##    elif event_line.EVENTMSGACTIONTYPE == 6:
##        p1_name  = None; p2_name = None;
##    elif event_line.EVENTMSGACTIONTYPE == 7:
##        p1_name  = None; p2_name = None;
##    elif event_line.EVENTMSGACTIONTYPE == 8:
##        p1_name  = None; p2_name = None;
##    elif event_line.EVENTMSGACTIONTYPE == 9:
##        p1_name  = None; p2_name = None;
##    elif event_line.EVENTMSGACTIONTYPE == 10:
##        p1_name  = None; p2_name = None;
    elif event_line.EVENTMSGACTIONTYPE == 11:
        t1 = 'turnover'
        p1_team, d1 = descripsAndTeams(event_line)
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
        e1_name = 'SHOTCLOCK'
        p2_name = None
    elif event_line.EVENTMSGACTIONTYPE == 39:
        t1 = 'step out of bounds'
        p1_team, d1 = descripsAndTeams(event_line)
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
        e1_name = 'OOB'
        p2_name = None
    elif event_line.EVENTMSGACTIONTYPE == 41:
        t1 = 'poss lost ball'
        p1_team, d1 = descripsAndTeams(event_line)
        p1_name = playerFromTOBegin(event_line, p1_team, t1)
        e1_name = 'LOSTBALL'
        p2_name = None
    else:
        # OK, attempted catch-all
        # way too many types; kick out to GameEvents level to fix
        p1_team, d1 = descripsAndTeams(event_line)
        p1_name = d1.split(' Turnover')[0]
        e1_name = 'TO-UNKN'
        p2_name = None
        

    if p1_name:
        entries.append({'Event' : e1_name,
                        'Player' : p1_name,
                        'Team' : p1_team,
                        'DESCRIPTION' : d1,
                        'EVENTNUM' : int(event_line.EVENTNUM),
                        'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                        'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                        'PERIOD' : int(event_line.PERIOD),
                        'GAMECLOCK' : int(event_line.GAMECLOCK),
                        })
    else:
        entries.append({'Event' : None,
                    'Player' : None,
                    'Team' : p1_team,
                    'DESCRIPTION' : d1,
                    'EVENTNUM' : int(event_line.EVENTNUM),
                    'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                    'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                    'PERIOD' : int(event_line.PERIOD),
                    'GAMECLOCK' : int(event_line.GAMECLOCK),
                    })
    if p2_name:
        entries.append({'Event' : e2_name,
                        'Player' : p2_name,
                        'Team' : p2_team,
                        'DESCRIPTION' : d2,
                        'EVENTNUM' : int(event_line.EVENTNUM),
                        'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                        'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                        'PERIOD' : int(event_line.PERIOD),
                        'GAMECLOCK' : int(event_line.GAMECLOCK),
                        })

    return(entries)


def splitSub(event_line):
    team, descrip = descripsAndTeams(event_line)
    entries = []
    d = descrip.split()
    for_loc = d.index('FOR')
    entries.append({'Event' : 'SUB_IN',
                    'Player' : ' '.join(d[1:for_loc]),
                    'Team' : team,
                    'DESCRIPTION' : descrip,
                    'EVENTNUM' : int(event_line.EVENTNUM),
                    'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                    'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                    'PERIOD' : int(event_line.PERIOD),
                    'GAMECLOCK' : int(event_line.GAMECLOCK),
                    })
    entries.append({'Event' : 'SUB_OUT',
                    'Player' : ' '.join(d[for_loc+1:]),
                    'Team' : team,
                    'DESCRIPTION' : descrip,
                    'EVENTNUM' : int(event_line.EVENTNUM),
                    'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                    'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                    'PERIOD' : int(event_line.PERIOD),
                    'GAMECLOCK' : int(event_line.GAMECLOCK),
                    })
    return(entries)


def splitJumpBall(event_line):
    # Need to figure out what to do with this.
    # Not particularly important, so putting off
    team, descrip = descripsAndTeams(event_line)
    entries = []
    d = descrip[10:]
    d = d.split(' vs. ')
    p1_name = d[0]
    d = d[1].split(': Tip to ')
    p2_name = d[0]
    p3_name = d[1]

    entries.append({'Event' : 'JUMPBALL',
                    'Player' : None,
                    'Team' : None,
                    'DESCRIPTION' : descrip,
                    'EVENTNUM' : int(event_line.EVENTNUM),
                    'EVENTMSGTYPE' : int(event_line.EVENTMSGTYPE),
                    'EVENTMSGACTIONTYPE' : int(event_line.EVENTMSGACTIONTYPE),
                    'PERIOD' : int(event_line.PERIOD),
                    'GAMECLOCK' : int(event_line.GAMECLOCK),
                    })

    return(entries)


def descripsAndTeams(event_line, t1='', num_players=1):
    if event_line.HOMEDESCRIPTION and \
       event_line.HOMEDESCRIPTION.lower().find(t1) > -1:
        p1_team = 'home'; d1 = event_line.HOMEDESCRIPTION;
        if num_players == 2:
            p2_team = 'away'; d2 = event_line.VISITORDESCRIPTION;
    elif event_line.VISITORDESCRIPTION and \
         event_line.VISITORDESCRIPTION.lower().find(t1) > -1:
        p1_team = 'away'; d1 = event_line.VISITORDESCRIPTION;
        if num_players == 2:
            p2_team = 'home'; d2 = event_line.HOMEDESCRIPTION;
    else:
        p1_team = 'neutral'
        d1 = event_line.NEUTRALDESCRIPTION  
    if num_players == 1:
        return(p1_team, d1)
    elif num_players == 2:
        return(p1_team, d1, p2_team, d2)


def descripsAndTeamsBasic(event_line, num_players = 1):
    if event_line.HOMEDESCRIPTION:
        p1_team = 'home'; d1 = event_line.HOMEDESCRIPTION;
        if num_players == 2:
            p2_team = 'away'; d2 = event_line.VISITORDESCRIPTION;
    elif event_line.VISITORDESCRIPTION:
        p1_team = 'away'; d1 = event_line.VISITORDESCRIPTION;
        if num_players == 2:
            p2_team = 'home'; d2 = event_line.HOMEDESCRIPTION;
    else:
        p1_team = 'neutral'
        d1 = event_line.NEUTRALDESCRIPTION
    if num_players == 1:
        return(p1_team, d1)
    elif num_players == 2:
        return(p1_team, d1, p2_team, d2)


def playerFromTOBegin(event_line, hORa, search_term):
    if hORa == 'home':
        d = event_line.HOMEDESCRIPTION
    elif hORa == 'away':
        d = event_line.VISITORDESCRIPTION
    else:
        d = event_line.NEUTRALDESCRIPTION
    if d:
        i = d.lower().find(search_term)
        player = d[:i-1]
    else:
        player = 'GameEvent'
    return(player)


def playerFromShot(event_line, hORa):
    shot_dist_match = re.compile(r"[0-9]+'")
    shot_pt_match = re.compile(r"[2|3]PT")
    if hORa == 'home':
        d = event_line.HOMEDESCRIPTION
    elif hORa == 'away':
        d = event_line.VISITORDESCRIPTION
    if d[:4].lower() == 'miss':
        d = d[5:]
    if d.find('Free Throw') > -1:
        player = d.split('Free Throw')[0].strip()
    elif re.search(shot_dist_match, d):
        player = re.split(shot_dist_match, d)[0].strip()
    elif re.search(shot_pt_match, d):
        player = re.split(shot_pt_match, d)[0].strip()
    else:
        # Everything without the first two examples have
        # a double space..
        player = d.split("  ")[0].strip()
    return(player)


def playerFromAst(event_line, hORa):
    if hORa == 'home':
        d = event_line.HOMEDESCRIPTION
    elif hORa == 'away':
        d = event_line.VISITORDESCRIPTION
    if d.lower().find('ast') > -1:
        d = d_split = d.split(') (')
        d = re.split('[0-9]+', d[1])
        player = d[0][:-1]
    else:
        player = None
    return(player)


def foulTypePhrase(event_line):
    if event_line.EVENTMSGACTIONTYPE == 1:
        t1 = 'p.foul'
    elif event_line.EVENTMSGACTIONTYPE == 2:
        t1 = 's.foul'
    elif event_line.EVENTMSGACTIONTYPE == 3:
        t1 = 'l.b.foul'
    elif event_line.EVENTMSGACTIONTYPE == 4:
        t1 = 'off.foul'
    elif event_line.EVENTMSGACTIONTYPE == 26:
        t1 = 'offensive charge foul'
    elif event_line.EVENTMSGACTIONTYPE == 28:
        t1 = 'personal take foul'
    elif event_line.EVENTMSGACTIONTYPE == 29:
        t1 = 'shooting block foul'
    else:
        t1 = None

    return(t1)


def playerNameFromDescrip(descrip,
                          player_last_names,
                          player_pbp_names,
                          team_names=[]):
    d_split = descrip.split()
    p_name = ''
    for i,w in enumerate(d_split):
        if w in team_names or \
           w in player_last_names or\
           w in player_pbp_names:
            p_name = ' '.join(d_split[:i+1])
    return(p_name)
            
    


####################################################
### PBP Splitting
####################################################

def splitFullPbpBySubsQuarters(pbp_df):
    events_list = []
    cur_events_list = []
    count = 0
    while count < pbp_df.shape[0]:
        if pbp_df.EVENTMSGTYPE[count] in [8, 13]:
            events_list.append(cur_events_list)
            cur_events_list = [count]
        else:
            cur_events_list.append(count)
        count += 1
    return(events_list)


def splitEventsBySubsQuarters(events):
    events_list = []
    cur_events_list = []
    count = 0
    while count < len(events):
        if events[count]['EVENTMSGTYPE'] == 8:
            if cur_events_list:
                events_list.append(cur_events_list)
                cur_events_list = []
            events_list.append([count, count + 1])
            count += 1
        elif events[count]['EVENTMSGTYPE'] == 13:
            if cur_events_list:
                cur_events_list.append(count)
                events_list.append(cur_events_list)
                cur_events_list = []
            else:
                events_list.append([count])
        else:
            cur_events_list.append(count)
        count += 1
    return(events_list)
            
