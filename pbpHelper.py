
import re
import pandas
from momentsHelper import definePeriods


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

EVENTS_LIST = ['pass',
               'steal',
               'rebound',
               'block',
               'foul',
               'shot',
               'turnover',
               'sub',
               'free_throw',
               'timeout']


def preprocessEvents(pbp):
    """

    """
    
    play_by_play = pbpDict2Df(pbp['play_by_play'])
    player_info = prepPlayerInfo(pbp['player_info'])
    events = pbpEventsExtractor(play_by_play, player_info)
    events = addGameClock(events)
    events = addQuarters(events)

    return(events)


def pbpEventsExtractor(play_by_play, player_info,
                       el = EVENTS_LIST):
    """
    Extract all event types from pbp.
    Return as dataframe with associated pbp timestamp.
    """
    
    # Initilize variables
    events = pandas.DataFrame(data = [(eid, t) for (eid, t) in \
                                      zip(range(play_by_play.shape[0]),
                                          play_by_play.PCTIMESTRING)],
                              columns = ['Index', 'PlayClock'])
    
    # Iterate over teams
    for t in ['home', 'away']:
        if t == 'home':
            evs = play_by_play.HOMEDESCRIPTION
        if t == 'away':
            evs = play_by_play.VISITORDESCRIPTION
        # Iterate over event types
        for ev_type in el:
            df = eventFromPbp(evs, t, ev_type)
            events = events.merge(df)
        # Determine player
        if player_info:
            df = playersFromEvents(evs, t, player_info)
            events = events.merge(df)
    
    return(events)


def prepPlayerInfo(pi):
    """
    Lots to do here:
        - need to include home / away info for player lookups
        - the 
    """

##    pi = pbp['player_info']
    pi['PLAYER_NAME']
    pbp_name_ids = {n : \
                    {'pid' : i,
                     'hORv' : '',
                     'pbp_name' : n.split(' ')[1],
                     } for (n, i) in zip(pi['PLAYER_NAME'], pi['PLAYER_ID'])}
    return(pbp_name_ids)



def eventFromPbp(events, t, ev_type):
    """ Extract a single event type from the list of events"""
    # Check if passed ev_type is valid
    if ev_type not in EVENTS_LIST:
        msg = 'Invald event type passed'
        raise AttributeError, msg
        
    # Set the search pattern
    if ev_type == 'pass':
        pat = re.compile(r'Pass|PASS')
    elif ev_type == 'steal':
        pat = re.compile(r'STEAL|Steal')
    elif ev_type == 'rebound':
        pat = re.compile(r'REBOUND|Rebound')
    elif ev_type == 'block':
        pat = re.compile(r' BLOCK ')
    elif ev_type == 'foul':
        pat = re.compile(r'FOUL|Foul')
    elif ev_type == 'shot':
        pat = re.compile(r'Shot|Dunk|Layup')
    elif ev_type == 'turnover':
        pat = re.compile(r'Turnover')
    elif ev_type == 'sub':
        pat = re.compile(r'SUB:')
    elif ev_type == 'free_throw':
##        pat = re.compile(r'Free Throw')
        pat = re.compile(r'Free Throw [1-3] of [1-3]')
    elif ev_type == 'timeout':
        pat = re.compile(r'Timeout')
        
    # Find which events are the type indicated
    event_indicator = []
    for ev in events:
        if not ev:
            event_indicator.append(False)
        elif re.search(pat, ev):
            event_indicator.append(True)
        else:
            event_indicator.append(False)
    event_indicator = [(eid, ei) for (eid, ei) in zip(range(len(events)),
                                                      event_indicator)]
    event_indicator = pandas.DataFrame(data = event_indicator,
                                       columns = ['Index', '_'.join([t, ev_type])])
    return(event_indicator)


def playersFromEvents(events, team, player_info):
    """
    """
    # Restrict to only players on team if team provided
    if player_info.values()[0]['hORv']:
        player_info = [p for p in player_info \
                       if p['hORv']==t]
    ps = re.compile('|'.join([p['pbp_name'] for p in player_info.values()]))

    # Create reverse lookup
    player_lookup = {p['pbp_name'] : p['pid'] for p in player_info.values()}

    # Search for players in events, append pids
    player_events = []
    for e in events:
        if e:
            p_names = re.findall(ps, e)
            pids = [player_lookup[p_name] for p_name in p_names]
        else:
            pids = []
        player_events.append(pids)

    # Convert to pandas.DataFrame
    player_events = [(eid, pe) for (eid, pe) in zip(range(len(events)),
                                                    player_events)]
    player_events = pandas.DataFrame(data = player_events,
                                     columns = ['Index', '_'.join([team, 'pids'])])
    return(player_events)


def addGameClock(events):
    # Add game clock info, quarters
    pc = events.PlayClock
    t = [(p.split(':')[0], p.split(':')[1]) for p in pc]
    times = pandas.DataFrame(data = zip(events.Index,
                                        [60 * int(m) + int(s) for (m, s) in t]),
                             columns = ['Index', 'game_clock'])
    events = events.merge(times)
    return(events)


def addQuarters(events):
    qrs = definePeriods(events, main_key = 'Index', dtype = 'pbp')
    events = pandas.merge(events, qrs)
    return(events)


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
