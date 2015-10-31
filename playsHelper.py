

def matchEvents2Segs(segments_info, events_info, log=False):

    s_curr = 0
    s_keys = segments_info.keys()
    e_s_lookup = {}
    for i, t, q in zip(events_info.index, events_info.game_clock, events_info.Quarter):
        while True:
            if s_curr >= len(s_keys):
                if log:
                    msg = 'overshot ' + str(s_curr)
                else:
                    msg = None
                e_s_lookup[i] = msg
                break
            if t <= segments_info[s_keys[s_curr]]['StartTime']:
                if t >= segments_info[s_keys[s_curr]]['EndTime']:
                    e_s_lookup[i] = s_keys[s_curr]
                    break
                else:
                    if q < segments_info[s_keys[s_curr]]['Quarter']:
                        e_s_lookup[i] = None
                        break
                    else:
                        s_curr += 1
            else:
                if q > segments_info[s_keys[s_curr]]['Quarter']:
                    s_curr += 1
                else:
                    if log:
                        msg = 'miss ' + str(s_curr)
                    else:
                        msg = None
                    e_s_lookup[i] = msg
                    break
    
    return(e_s_lookup)
