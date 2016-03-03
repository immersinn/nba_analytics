
import numpy
import pandas


def matchEventsMoments(game_segments):

    # Segments meta
    seg_ssq = {}
    for k in game_segments._moments:
        seg_ssq[k.ind] = {'Start' : k.start,
                          'End' : k.end,
                          'Quarter' : k.period,
                          'Players' : k._player_ids}

    # Play by Play meta
    pbp_ssq = {}
    for k in game_segments._events:
        pbp_ssq[k.ind] = {'Start' : k.start,
                          'End' : k.end,
                          'Quarter' : k.period,
                          'Type': k.event_type,
                          'Players' : k._player_ids}
        
    # Find Matches
    matches = []
    e_matched = []
    s_matched = []
    qs = set([seg_ssq[k]['Quarter'] for k in seg_ssq.keys()])

    for q in qs:
        segs = {k:v for k,v in seg_ssq.items() if v['Quarter'] == q}
        pbps = {k:v for k,v in pbp_ssq.items() if v['Quarter'] == q}
        s_keys = sorted(segs.keys())
        p_keys = sorted(pbps.keys())
        # Last events of a quarter is always with the
        # last moment of a quarter because last events
        # includes 'End of Period' event
        s = pbps[p_keys[-1]]['Start'] \
            if pbps[p_keys[-1]]['Start'] >= segs[s_keys[-1]]['Start'] \
            else segs[s_keys[-1]]['Start']
        e = pbps[p_keys[-1]]['End'] \
            if pbps[p_keys[-1]]['End'] <= segs[s_keys[-1]]['End'] \
            else segs[s_keys[-1]]['End']
        matches.append({'EventsId' : p_keys[-1],
                        'MomentId' : s_keys[-1],
                        'Start' : s,
                        'End' : e,
                        'Period' : pbps[p_keys[-1]]['Quarter']})
        e_matched.append(p_keys[-1])
        s_matched.append(s_keys[-1])
        cur_seg_ind = -2

        for pk in reversed(p_keys[:-1]):
            tmp_seg_ind = cur_seg_ind
            cur_pbp = pbps[pk]
            if cur_pbp['Type'] != 'REGULAR_PLAY':
                continue
            while True:
                if abs(tmp_seg_ind) > len(s_keys):
                    break
                cur_seg = segs[s_keys[tmp_seg_ind]]
                if cur_seg['Players'] == cur_pbp['Players']:
                    # Check to see if start time of either current portion resides
                    # within range of other portion
                    if cur_seg['Start'] <= cur_pbp['Start'] and \
                       cur_seg['Start'] >= cur_pbp['End']:
                        matches.append({'EventsId' : pk,
                                        'MomentId' : s_keys[tmp_seg_ind],
                                        'Start' : cur_pbp['Start'],
                                        'End' : cur_pbp['End'],
                                        'Period' : cur_pbp['Quarter']})
                        e_matched.append(pk)
                        s_matched.append(s_keys[tmp_seg_ind])
                        cur_seg_ind = tmp_seg_ind - 1
                        break
                    elif cur_pbp['Start'] <= cur_seg['Start'] and \
                         cur_pbp['Start'] >= cur_seg['End']:
                        matches.append({'EventsId' : pk,
                                        'MomentId' : s_keys[tmp_seg_ind],
                                        'Start' : formatMomentTime(cur_seg['Start'], 'start'),
                                        'End' : formatMomentTime(cur_seg['End'], 'end'),
                                        'Period' : cur_seg['Quarter']})
                        e_matched.append(pk)
                        s_matched.append(s_keys[tmp_seg_ind])
                        cur_seg_ind = tmp_seg_ind - 1
                        break
                    else:
                        tmp_seg_ind -= 1
                else:
                        tmp_seg_ind -= 1

    e_not_matched = set(pbp_ssq.keys()).difference(e_matched)
    s_not_matched = set(seg_ssq.keys()).difference(s_matched)

    for enm in e_not_matched:
        matches.append({'EventsId' :enm,
                        'MomentId' : -1,
                        'Start' : pbp_ssq[enm]['Start'],
                        'End' : pbp_ssq[enm]['End'],
                        'Period' : pbp_ssq[enm]['Quarter']})
    for snm in s_not_matched:
        matches.append({'EventsId' : -1,
                        'MomentId' : snm,
                        'Start' : formatMomentTime(seg_ssq[snm]['Start'], 'start'),
                        'End' : formatMomentTime(seg_ssq[snm]['End'], 'end'),
                        'Period' : seg_ssq[snm]['Quarter']})

    matches = pandas.DataFrame(matches, dtype=int)
    matches.sort_index(by=['Period', 'Start', 'EventsId'],
                       ascending = [True, False, True],
                       inplace=True)
    matches.index = range(matches.shape[0])
    
    return(matches)


def matchEventsMomentsTransitions(s, bt_class, method=''):

    """
        matches = mergeMatches(matches, matches_t3)
        non_pass_pt = [p for (t,p) in matches]
        events = [i for i in range(len(pos_events)) if i in non_pass_pt]
        passes = [i for i in range(len(pos_events)) if i not in non_pass_pt]
    """

    bt = []
    
    if s.eventsId == None:
        nMomTrans = len(s.moment_ball_transitions)
        events = []
        passes = [i for i in range(nMomTrans)]
        non_pass_pt = []
        
    elif s.momentId == None:
        events = []
        passes = []
        nMomTrans = 0

        for t in s.events_ball_transitions:
            new_dict = t.copy()
            _ = new_dict.pop('EventId')
            eid = new_dict['ind']
            new_dict = applyMissingMomentKeys(new_dict)
            new_dict['eventId'] = eid
            bt.append(bt_class(new_dict))      
        
    else:

        # Number of Transitions
        nMomTrans = len(s.moment_ball_transitions)
        nEveTrans = len(s.events_ball_transitions)

        # First Pass: "Exact" Match
        start = 0
        matches = []
        for et in s.events_ball_transitions:
            for j, mt in enumerate(s.moment_ball_transitions[start:]):
                if pbpPosMatch(et, mt):
                    matches.append((et['ind'], mt['ind']))
                    start = start + j + 1
                    break


        # Second Pass: Inbounds plays
        matches_t2 = []
        matched_trans = [i for (i,j) in matches]
        unmatched = [i for i in range(nEveTrans) \
                     if i not in set(matched_trans)]
        for i in unmatched:
            low = lastMatchBelow(matches, i)
            high = firstMatchAbove(matches, i)
            if high - low == 2:
                matches_t2.append((i, low + 1))
            else:
                for j in range(low + 1, high):
                    if inboundsMatch(s.events_ball_transitions[i],
                                     s.moment_ball_transitions[j]):
                        matches_t2.append((i,j))
                        break

        updateEventsInboundTransition(s, matches_t2)
        matches = mergeMatches(matches, matches_t2)


        # Third Pass:  Everything else (hopefully)
        matches_t3 = []
        matched_trans = [i for (i,j) in matches]
        unmatched = [i for i in range(nEveTrans) \
                     if i not in set(matched_trans)]
        for i in unmatched:
            low = lastMatchBelow(matches, i)
            high = firstMatchAbove(matches, i)
            if high - low == 2:
                matches_t2.append((i, low + 1))
            else:
                for j in range(low+1, high):
                    if halfMatch(s.events_ball_transitions[i],
                                 s.moment_ball_transitions[j]):
                        matches_t3.append((i,j))
                        break

        matches = mergeMatches(matches, matches_t3)
        non_pass_pt = [p for (t,p) in matches]
        events = [i for i in range(nMomTrans) if i in non_pass_pt]
        passes = [i for i in range(nMomTrans) if i not in non_pass_pt]

            

    # Merge events and moment transitions
    for i in range(nMomTrans):
        if i in non_pass_pt:
            w = non_pass_pt.index(i)
            e,m = matches[w]
            new_dict = s.events_ball_transitions[e].copy()
            _ = new_dict.pop('EventId')
            eid = new_dict['ind']
            new_dict.update(s.moment_ball_transitions[m].copy())
            new_dict['eventId'] = eid; new_dict['momentId'] = i
        else:
            new_dict = {k : v for (k,v) in \
                        s.moment_ball_transitions[i].items()}
            new_dict = applyMissingEventKeys(new_dict)
            new_dict['momentId'] = i
        bt.append(bt_class(new_dict))

    s._ball_transitions = bt


def transitions2graph(ball_transitions):
    edges = []
    for bt in ball_transitions:
        if bt['TransitionType'] == 'Pass':
            edges.append(passTransitionIntoEdge_v01(bt))
        else:
            edges.extend(splitTransitionIntoEdges_v01(bt))
    return(edges)


def passTransitionIntoEdge_v01(bt):
    return({'To' : bt['ToPlayer'],
            'From' : bt['FromPlayer'],
            'Start' : bt['StartGameClock'],
            'End' : bt['EndGameClock'],
            'Period' : bt['Period']})


def splitTransitionIntoEdges_v01(bt):
    ttypes = bt['TransitionType'].split('-')
    times = gcFromBT(bt)
    
    if ttypes[0].find('Miss') > -1:
        # create TO FAIL edge
        to = 'FAIL'
    elif ttypes[0].find('Made') > -1:
        # create TO SUCCESS edge
        to = 'SUCCESS'
    elif ttypes[0] == 'Turnover':
        # create TO TURNOVER edge
        to = 'TURNOVER'
    else:
        to = bt['TransitionType']

    if ttypes[1] in ['Rebound', 'OffRebound', 'DefRebound']:
        # create FROM REBOUND edge
        fr = ttypes[1].upper()
    elif ttypes[1] == 'Inbounds':
        # create FROM INBOUNDS edge
        fr = 'INBOUNDS'
    elif ttypes[1] == 'Steal':
        # create FROM STEAL edge
        fr = 'STEAL'

    edge1 = {'From' : bt['FromPlayer'],
             'To' : to,
             'Start' : times[0],
             'End' : numpy.float64(-1),
             'Period' : bt['Period']}

    edge2 = {'From' : fr,
             'To' : bt['ToPlayer'],
             'Start' : numpy.float64(-1),
             'End' : times[1],
             'Period' : bt['Period']}

    return([edge1, edge2])



def gcFromBT(bt):
    """Return appropriate GameClock from a ball transition dict"""
    if bt['StartGameClock']:
        return([bt['StartGameClock'],
                bt['EndGameClock']])
    else:
        return([bt['GameClock'],
                bt['GameClock']])
    


def applyMissingEventKeys(new_dict):
    new_dict['TransitionType'] = 'Pass'
    new_dict['TransSubType'] = ''
    new_dict['GameClock'] = numpy.int64(-1)
    new_dict['eventId'] = numpy.int64(-1)
    return(new_dict)


def applyMissingMomentKeys(new_dict):
    new_dict['StartIndx'] = numpy.int64(-1)
    new_dict['EndIndx'] = numpy.int64(-1)
    new_dict['StartGameClock'] = numpy.float64(-1)
    new_dict['EndGameClock'] = numpy.float64(-1)
    new_dict['momentId'] = numpy.int64(-1)
    return(new_dict)


def formatMomentTime(time, sORe):
    if sORe == 'start':
        return(int(numpy.floor(time)))
    elif sORe == 'end':
        return(int(numpy.ceil(time)))


def pbpPosMatch(et, mt):
    if et['FromPlayer'] == mt['FromPlayer'] and \
       et['ToPlayer'] == mt['ToPlayer'] and \
       abs(et['GameClock'] - mt['EndGameClock']) < 5:
##       abs(et['GameClock'] - mt['StartGameClock']) < 3 and \
            return(True)
    else:
        return(False)
    

def inboundsMatch(et, mt):
    if et['FromPlayer'] == mt['FromPlayer'] and \
       abs(et['GameClock'] - mt['EndGameClock']) < 7 and \
       et['ToPlayer'] == 'TBD':
            return(True)
    else:
        return(False)
    
    
def halfMatch(et, mt):
    if et['FromPlayer'] == mt['FromPlayer'] and \
       abs(et['GameClock'] - mt['EndGameClock']) < 7:
            return(True)
    elif et['ToPlayer'] == mt['ToPlayer'] and \
         abs(et['GameClock'] - mt['EndGameClock']) < 7:
            return(True)
    else:
        return(False)
    
    
def lastMatchBelow(matches, i):
    last = 0
    for t,p in matches:
        if t < i:
            last = p
        else:
            break
    return(last)


def firstMatchAbove(matches, i):
    last = i
    for t,p in matches:
        if t > i:
            last = p
            break
    return(last)


def mergeMatches(matches0, matches1):
    merged = []
    m0_ind = 0
    m1_ind = 0
    while m0_ind < len(matches0) and m1_ind < len(matches1):
        if matches0[m0_ind][0] < matches1[m1_ind][0]:
            merged.append(matches0[m0_ind])
            m0_ind += 1
        else:
            merged.append(matches1[m1_ind])
            m1_ind += 1
    for m in matches0[m0_ind:]:
        merged.append(m)
    for m in matches1[m1_ind:]:
        merged.append(m)
    return(merged)


def updateEventsInboundTransition(s, inbounds_matches):
    # transitions are data with 'TBD'
    # pos_events are ball trans from movement data
    # matches_t2 are (t, p) matches, where t is the trans index
    # and p is the pos index
    for ei, mi in inbounds_matches:
        s.events_ball_transitions[ei]['ToPlayer'] = \
        s.moment_ball_transitions[mi]['ToPlayer']


def updateMomentPassEvents(tar):
    tar['TransitionType'] = 'Pass'
