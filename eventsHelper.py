

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
    if 'play_by_play' in list(pbp.keys()):
        for i in sorted([int(k) for k in list(pbp['play_by_play'].keys())]):
                p_ord.append(pbp['play_by_play'][str(i)])
    else:
        for i in sorted([int(k) for k in list(pbp.keys())]):
                p_ord.append(pbp[str(i)])
    pbp = pandas.DataFrame(p_ord,
                           columns=HEADER)

    return(pbp)


def addIndex(pbp):
    ind = pandas.DataFrame(data = list(range(pbp.shape[0])),
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

    if event_line.EVENTMSGTYPE == -1:
        state = 'BREAK'
    elif event_line.EVENTMSGTYPE == 1:
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

    # The assist pass comes before the shot
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

    # Add the shot
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
### Who's on first?
####################################################


def playersForEventsGame(ge_instance):
    periods = ge_instance.periods
    team_names = [ge_instance.team_info['home']['nickname'].lower(),
                  ge_instance.team_info['away']['nickname'].lower()]
    for ev in ge_instance._events:
        ev['PlayersOnCourt'] = {}
    for q in periods:
        quarter_events = [ev for ev in ge_instance._events if \
                          ev['PERIOD'] == q]
        for team in ['home', 'away']:
            players = playersForEventsQuarter(quarter_events,
                                              team,
                                              ge_instance.name2id,
                                              team_names)
            for i,ev in enumerate(quarter_events):
                ev['PlayersOnCourt'][team] = players[i]


def playersForEventsQuarter(qes, team, lookup, team_names):
    players = [set() for _ in qes]
    for i,s in enumerate(qes):
        if s['Team'] == team:
            if s['Event'] not in ['SUB_IN', 'SUB_OUT']:
                if s['Player'].lower() not in team_names:
                    p = s['Player']
                    players[i].update([p])
                    for j in reversed(list(range(i))):
                        if qes[j]['Player'] != p:
                            players[j].update([p])
                        else:
                            break
                    for j in range(i+1, len(qes)):
                        if qes[j]['Player'] != p:
                            players[j].update([p])
                        else:
                            break
                else:
                    pass
            elif s['Event'] == 'SUB_OUT':
                p = s['Player']
                players[i].update([p])
                for j in reversed(list(range(i))):
                    if qes[j]['Player'] != p:
                        players[j].update([p])
                    else:
                        break
            elif s['Event'] == 'SUB_IN':
                p = s['Player']
                players[i].update([p])
                for j in range(i+1, len(qes)):
                    if qes[j]['Player'] != p:
                        players[j].update([p])
                    else:
                        break
        else:
            pass
    players = [sorted([lookup[p] for p in pl]) for pl in players]
    return(players)


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


####################################################
### Events Transition Network Classes, Modules
####################################################


class TransitionsFinder:


    def __init__(self, events, null_event):
        self.events = events
        self.null = null_event
        self.indx = 0
        self.max_indx = len(self.events)
        self.event_dict = {}
        self.event_count = 0
        self.current = []


    def getTransitions(self,):
        while self.indx < self.max_indx:
            ne = SinglePosChangeFinder(self.events,
                                       self.null,
                                       self.indx,)
            ne.getPosChange()
            self.current.extend(ne.transitions)
            self.indx = ne.indx + 1
            if ne.state == 'EOL':
                if self.current:
                    new = {}
                    new['Period'] = self.current[0]['period']
                    new['Start'] = self.current[0]['gc']
                    new['End'] = self.current[-1]['gc']
                    new['TransitionsData'] = self.current
                    self.event_dict[self.event_count] = new
                    self.event_count += 1
                    self.current = []


####################


MAIN_EVENTS = ['MissShot',
               'MadeShot',
               'Turnover',
               'Foul']
STOP_EVENTS = ['QuarterEnd',
               'Sub',
               'BREAK']


class SinglePosChangeFinder:


    def __init__(self, events_inst, null_event, start_indx=0):
        self.events = events_inst
        self.null = null_event
        self.indx = start_indx
        self.max_indx = len(events_inst)
        self.transitions = []
        #self.initState()


    def getPosChange(self,):
        self.initState()
        self.evalState()


    def initState(self):
        self.state = ''
        self.indx -= 1
        #while not self.state and self.indx < self.max_indx - 1:
        while not self.state:
            self.indx += 1
            self.determineState()


    def determineState(self,):
        self.setCurrEvent()
        event_msg_state = detEventType(self.current)
        if event_msg_state in MAIN_EVENTS:
            self.state = event_msg_state
        elif event_msg_state in STOP_EVENTS:
            self.state = 'EOL'


    def setCurrEvent(self, event = {}, index = -1):
        if index < 0:
            index = self.indx
        if event:
            self.current = event
        elif index < len(self.events):
            self.current = self.events[index]
        else:
            self.current = self.null


    def evalState(self):
        if self.state == 'MadeShot':
            self.evalMadeShot()
        elif self.state == 'MissShot':
            self.evalMissShot()
        elif self.state == 'Turnover':
            self.evalTurnover()
        elif self.state == 'Foul':
            self.evalFoulShots()
        elif self.state == 'EOL':
            pass


    def getGameClock(self,):
        return(self.current.GAMECLOCK)


    def getQuarter(self,):
        return(self.current.PERIOD)


    def getPlayer(self,):
        if self.current.pid:
            return(self.current.pid)
        else:
            return(self.current.Player)


    def updateTransition(self,):
        overall = {'from' : self.fr_player,
                   'to' : self.to_player,
                   'ttype' : self.trans_type,
                   'period' : self.getQuarter(),
                   'gc' : self.getGameClock()}
        self.transitions.append(overall)
        if self.trans_type.find('Rebound') > -1:
            self.transitions.append({'from' : 'REBOUND',
                                     'to' : self.to_player,
                                     'ttype' : 'Rebound',
                                     'period' : self.getQuarter(),
                                     'gc' : self.getGameClock()})


    def addInboundsTransition(self,):
        if self.state == 'MadeShot':
            self.transitions.append({'from' : self.fr_player,
                                     'to' : 'TBD',
                                     'ttype' : 'MadeShot-Inbounds',
                                     'period' : self.getQuarter(),
                                     'gc' : self.getGameClock()})
        self.transitions.append({'from' : 'INBOUNDS',
                                 'to' : 'TBD',
                                 'ttype' : 'Inbounds',
                                 'period' : self.getQuarter(),
                                 'gc' : self.getGameClock()})


    def evalMadeShot(self):
        self.evalAssist()
        self.fr_player = self.getPlayer()
        self.transitions.append({'to' : 'SUCCESS',
                                 'from' : self.fr_player,
                                 'ttype' : 'MadeShot',
                                 'period' : self.getQuarter(),
                                 'gc' : self.getGameClock()})
        self.evalShootFoul()
        if self.state == 'Foul':
            self.evalFoulShots()
        else:
            self.addInboundsTransition()


    def evalMissShot(self):
        self.fr_player = self.getPlayer()
        self.transitions.append({'to' : 'FAIL',
                                 'from' : self.fr_player,
                                 'ttype' : 'MissShot',
                                 'period' : self.getQuarter(),
                                 'gc' : self.getGameClock()})
        self.evalShootFoul()
        if self.state == 'Foul':
            self.evalFoulShots()
        else:
            self.evalRebound()
            if self.state == 'Transition':
                self.updateTransition()
            else:
                # Error
                pass


    def evalTurnover(self,):
        # The order in Events instance:
        # First comes the turnover
        # Second comes the steal (if present)

        self.fr_player = self.getPlayer()
        self.transitions.append({'to' : 'TURNOVER',
                                 'from' : self.fr_player,
                                 'ttype' : 'Turnover',
                                 'period' : self.getQuarter(),
                                 'gc' : self.getGameClock()})

        self.setCurrEvent(index = self.indx + 1)
        if self.current.Event == 'STEAL':
            self.to_player = self.getPlayer()
            self.transitions.append({'to' : self.to_player,
                                     'from' : 'TURNOVER',
                                     'ttype' : 'Steal',
                                     'period' : self.getQuarter(),
                                     'gc' : self.getGameClock()})
            self.trans_type = self.state + '-Steal'
            self.updateTransition()
        else:
            self.addInboundsTransition()


    def evalAssist(self,):
        # Assist comes first in Events instance
        # Flagged as a MadeShot
        # Update indx to move focus to the actual shot
        if self.current.Event == 'Assist':
            fr_player = self.getPlayer()
            self.indx += 1
            self.setCurrEvent()
            to_player = self.getPlayer()
            self.transitions.append({'to' : to_player,
                                     'from' : fr_player,
                                     'ttype' : 'Pass',
                                     'tsubtype' : 'Assist',
                                     'period' : self.getQuarter(),
                                     'gc' : self.getGameClock()})


    def evalShootFoul(self):
        # Looks if shooting foul occuring during shot
        self.setCurrEvent(index = self.indx + 1)
        if detEventType(self.current) == 'Foul':
            self.indx += 1
            self.state = 'Foul'


    def evalFoulShots(self):
        # Parses through foul shots and determines if
        # last one was made or missed
        self.setCurrEvent(index = self.indx + 1)
        if detEventType(self.current) == 'FreeThrow':
            descrip = self.current.DESCRIPTION
            if descrip.find('MISS') > -1:
                self.state = 'MissedFoul'
                self.fr_player = self.getPlayer()
            else:
                self.state = 'MadeFoul'
            self.indx += 1
            self.evalFoulShots()
        elif detEventType(self.current) == 'Sub':
            self.indx = self.indx + 2 # Subs come in pairs now
            self.state = 'EOL'
        elif detEventType(self.current) == 'BREAK':
            self.state = 'EOL'
            self.setCurrEvent()
        else:
            if self.state == 'MadeFoul':
                self.addInboundsTransition()
            elif self.state == 'MissedFoul':
                self.evalRebound()
                if self.state == 'Transition':
                    self.updateTransition()
            elif self.state == 'EOL':
                self.setCurrEvent()


    def evalRebound(self):
        self.setCurrEvent(index = self.indx + 1)
        if detEventType(self.current) == 'Rebound':
            self.to_player = self.current.pid
            self.trans_type = self.state + '-Rebound'
            self.state = 'Transition'
            self.indx += 1
