
import numpy
import pandas


def matchEventsMoments(game_segments):

    # Segments meta
    seg_ssq = {}
    for k in game_segments._moments:
        seg_ssq[k.ind] = {'Start' : k.start,
                          'End' : k.end,
                          'Quarter' : k.period}

    # Play by Play meta
    pbp_ssq = {}
    for k in game_segments._events:
        pbp_ssq[k.ind] = {'Start' : k.start,
                          'End' : k.end,
                          'Quarter' : k.period,
                          'Type': k.event_type}
        
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


def formatMomentTime(time, sORe):
    if sORe == 'start':
        return(int(numpy.floor(time)))
    elif sORe == 'end':
        return(int(numpy.ceil(time)))
