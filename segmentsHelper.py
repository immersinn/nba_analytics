

def matchEventsMoments(events, moments):

    # Segments meta
    seg_ssq = {}
    for k in moments.keys():
        seg_ssq[k] = {'Start' : int(moments[k]['StartTime']),
                      'Stop' : int(moments[k]['EndTime']),
                      'Quarter' : moments[k]['Quarter']}

    # Play by Play meta
    pbp_ssq = {}
    for k in events.keys():
        pbp_ssq[k] = {'Start' : events[k]['StartTime'],
                      'Stop' : events[k]['EndTime'],
                      'Quarter' : events[k]['Quarter']}
        
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
        # Last event of a quarter is always with the
        # last segment of a quarter
        matches.append((p_keys[-1], s_keys[-1]))
        e_matched.append(p_keys[-1])
        s_matched.append(s_keys[-1])
        cur_seg_ind = -2

        for pk in reversed(p_keys[:-1]):
            tmp_seg_ind = cur_seg_ind
            cur_pbp = pbps[pk]
            while True:
                if abs(tmp_seg_ind) > len(s_keys):
                    break
                cur_seg = segs[s_keys[tmp_seg_ind]]

                # Check to see if start time of either current portion resides
                # within range of other portion
                if cur_seg['Start'] <= cur_pbp['Start'] and \
                   cur_seg['Start'] >= cur_pbp['Stop']:
                    matches.append((pk, s_keys[tmp_seg_ind]))
                    e_matched.append(pk)
                    s_matched.append(s_keys[tmp_seg_ind])
                    cur_seg_ind = tmp_seg_ind - 1
                    break
                elif cur_pbp['Start'] <= cur_seg['Start'] and \
                     cur_pbp['Start'] >= cur_seg['Stop']:
                    matches.append((pk, s_keys[tmp_seg_ind]))
                    e_matched.append(pk)
                    s_matched.append(s_keys[tmp_seg_ind])
                    cur_seg_ind = tmp_seg_ind - 1
                    break
                else:
                    tmp_seg_ind -= 1

    e_not_matched = set(pbp_ssq.keys()).difference(e_matched)
    s_not_matched = set(seg_ssq.keys()).difference(s_matched)

    for enm in e_not_matched:
        matches.append((enm, -1))
    for snm in s_not_matched:
        matches.append((-1, snm))
    
    return(matches)


def mergeEventsMoments(events, segments):
    """
    Want this format:
    
    segment {'moment' : moment_data,
             'events' : events_data,
             'SegmentInfo' : {},
             'PlayerInfo' : {}
                 }

    """

    matches = matchEventsMoments(events, moments)
    paired_eve_mom = []

    for e,s in matches:
        
        if e > -1 and s > -1:
            new = {'eid' : e, 'events' : events[e],
                   'mid' : s, 'moment' : moments[s],
                   'Quarter' : events[e]['Quarter']}
        elif e == -1:
            new = {'eid' : -1, 'events' : None,
                   'mid' : s, 'moment' : moments[s],
                   'Quarter' : moments[s]['Quarter']}
        elif s == -1:
            new = {'eid' : e, 'events' : events[e],
                   'mid' : -1, 'moment' : None,
                   'Quarter' : events[e]['Quarter']}
            
        paired_eve_mom.append(new)

    return(paired_eve_mom)
