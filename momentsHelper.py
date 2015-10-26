
import numpy
import pandas


##################################################
#### Merge attributes extraction
##################################################


def overlapTimes(game_info):
    # Overlapping time stamps
    s_indx = numpy.where(moments_info.columns == 'StartTime')[0][0]
    e_indx = numpy.where(moments_info.columns == 'EndTime')[0][0]
    end_start_diff = [a - b for (a, b) in \
                      zip(game_info.ix[0:(game_info.shape[0]-2), e_indx], 
                          game_info.ix[1:(game_info.shape[0]-1), s_indx])]
    overlap = [(e, d < 0) for (e, d) in zip(game_info.ix[1:game_info.shape[0], 0], end_start_diff)]
    overlap.insert(0, (game_info.ix[0, 0], True))
    overlap = pandas.DataFrame(data = overlap,
                               columns = ['EventId', 'Overlap'])
    return(overlap)


def samePlayers(game_info):
    # Same player ids
    same_players = [(game_info.EventId[i], list(game_info.PlayerIds[i]) == list(game_info.PlayerIds[i-1])) \
                    for i in range(1, game_info.shape[0])]
    same_players.insert(0, (game_info.EventId[0], True))
    same_players = pandas.DataFrame(data = same_players,
                                    columns = ['EventId', 'SamePlayers'])
    return(same_players)


def defineSegments(game_info):
    # Define Segments
    segment_criteria = 'Player'
    seg_count = 0

    if segment_criteria == 'TimePlayer':
        t_indx = numpy.where(moments_info.columns == 'Overlap')[0][0]
        p_indx = numpy.where(moments_info.columns == 'SamePlayers')[0][0]
        seg_flag = [a & b for (a, b) in \
                          zip(game_info.ix[1:(game_info.shape[0]-1), t_indx], 
                              game_info.ix[1:(game_info.shape[0]-1), p_indx])]
    elif segment_criteria == 'Player':
        p_indx = numpy.where(moments_info.columns == 'SamePlayers')[0][0]
        seg_flag = [a for a in game_info.ix[1:(game_info.shape[0]-1), p_indx]]

    seg_flag.insert(0, True)
    segments = [0]
    for i in seg_flag[1:]:
        if not i:
            seg_count += 1
        segments.append(seg_count)
    segments = pandas.DataFrame(data = zip(game_info.EventId, segments),
                                columns = ['EventId', 'Segment'])
    return(segments)
    

def definePeriods(game_info, main_key = 'EventId', dtype = 'game_info'):
    # Define Quarters
    if dtype == 'game_info':
        s_indx = numpy.where(moments_info.columns == 'StartTime')[0][0]
        e_indx = numpy.where(moments_info.columns == 'EndTime')[0][0]
        qua_flag = [a < b and a < 20. and c > 670 for (a, b, c) in \
                          zip(game_info.ix[1:(game_info.shape[0]-2), e_indx], 
                              game_info.ix[2:(game_info.shape[0]-1), e_indx],
                              game_info.ix[2:(game_info.shape[0]-1), s_indx])]
    elif dtype == 'pbp':
        c_indx = numpy.where(game_info.columns == 'game_clock')[0][0]
        qua_flag = [a < b and a < 20. and b > 700 for (a, b) in \
                          zip(game_info.ix[1:(game_info.shape[0] - 2), c_indx], 
                              game_info.ix[2:(game_info.shape[0] - 1), c_indx])]
    qua_flag.insert(0, False)
    last = numpy.where(qua_flag)[0]

    # Currently we do not allow for overtime games;
    # We have not encountered one, and we're not sure 
    # if the method we have for splitting quarters is
    # tuned enough, so we want to flag anything at
    # the moment.
    if len(last) == 3:    
        quarters = numpy.repeat(0, game_info.shape[0])
        start = 0
        for q, row in enumerate(last):
            quarters[start:row+1] = q + 1
            start = row + 1
        quarters[start:] = q + 2
    else:
        err_msg = 'Incorrect number of quarters; possible overtime.'
        raise AttributeError, err_msg

    quarters = pandas.DataFrame(data = zip(game_info[main_key], quarters),
                                columns = [main_key, 'Quarter'])
    return(quarters)


##################################################
#### Build, Filter, Clean Moments:
#### Full Moments Preprocessing
##################################################


def preprocessMoments(moments):
    """
    moments_info = mergeGameInfoMoments(game_info, moments)
    """
    
    game_info = buildGameInfo(moments)
    game_info = filterGameInfo(game_info)
    
    moments_info = mergeGameInfoMoments(game_info, moments)
    moments_info = cleanMoments(moments_info)
    moments_info = defineSegsQs(moments_info)
    
    return(moments_info)


##################################################
#### Build, Filter, Clean Segments:
#### Full Segments Preprocessing
##################################################


def preprocessSegments(moments):
    """

    """
    moments_info = preprocessMoments(moments)
    segments_info = mergeSegments(moments_info)
    segments_info = cleanSegments(segments_info)

    return(segments_info)

    

##################################################
#### Data Merges: Moments
##################################################


def buildGameInfo(moments):
    # Start time for each moment
    st = pandas.DataFrame(data = [(e, mg.game_clock[0]) for (g, e, mg) in moments],
                         columns = ['EventId', 'StartTime'])
    # End time for each moment
    en = pandas.DataFrame(data = [(e, mg.game_clock[mg.shape[0]-1]) for (g, e, mg) in moments],
                         columns = ['EventId', 'EndTime'])
    # Player IDs for each moment
    pl = pandas.DataFrame(data = [(e, numpy.unique(mg.player_id)) for (g, e, mg) in moments],
                         columns = ['EventId', 'PlayerIds'])
    # Merge all three, and sort on the EventID
    game_info = pandas.merge(st, en)
    game_info = game_info.merge(pl)
    game_info = game_info.sort_index(by = 'EventId')
    return(game_info)
    
    
def filterGameInfo(game_info):
    # Filter out moments that are encompassed by other moments
    # (diff for entry 0 is 'NaN', so it stays)
    keep = [s !=0 or e != 0 for (s,e) in zip(game_info.StartTime.diff(),
                                             game_info.EndTime.diff())]
    game_info = game_info.ix[keep]

    # Remove moments where no time ellapses
    keep = [s != e for (s,e) in zip(game_info.StartTime,
                                    game_info.EndTime)]
    game_info = game_info.ix[keep]

    # Remove moments where > 11 Player Ids (no idea)
    #keep = [len(p) == 11 for p in game_info.PlayerIds]
    #game_info = game_info.ix[keep]

    # Reindex data
    game_info.index = range(game_info.shape[0])
    return(game_info)


def mergeGameInfoMoments(game_info, moments):
    """
    :type game_info: pandas.DataFrame
    :param game_info: contains meta-data for each game moment, 
                      data relationships between adjacent moments
    
    :type moments: list of tuples
    :param moments: (game_id, event_id, raw moments data) for each moment (event)
    
    :rtype gim_info: pandas.DataFrame
    :rparam gim_info: merging of game_info and moments by EventId
    
    Merge the moments raw data with the meta-data info for each (filtered)
    moment in game_info.
    """
    
    moments = pandas.DataFrame(data = [(e, m) for (g, e, m) in moments],
                               columns = ['EventId', 'MomentData'])
    gim_info = game_info.merge(moments)
    return(gim_info)


def defineSegsQs(moments_info):
    # Merge Overlap Info, Player Info, Segments, Quarters with game_info
    overlap = overlapTimes(moments_info)
    same_players = samePlayers(moments_info)
    moments_info = moments_info.merge(overlap)
    moments_info = moments_info.merge(same_players)
    segments = defineSegments(moments_info)
    quarters = definePeriods(moments_info)
    moments_info = moments_info.merge(segments)
    moments_info = moments_info.merge(quarters)
    return(moments_info)


##################################################
#### Data Merges: Segments
##################################################


def mergeSegments(moments_info):
    """
    :type moments_info: pandas.DataFrame
    :param moments_info: pre-processed Moments Information
    
    :rtype segments_info: pandas.DataFrame
    :rparam segments_info: meta info for each segment paired with the merged 
                              set of data from all moments in the segment.
                              
    Raw game moments often overlap with one another.  Additionally, it is useful
    to combine temporally adjacent sets of data for which players are consistent.
    We refer to the reduced set of adjacent moments data for which players remain
    consistent as a Game Segment.
    """
    
    segments_info = {}
    timestamps = set()
    for s in numpy.unique(moments_info.Segment):
        seg_info, timestamps = mergeSegment(moments_info[moments_info.Segment==s],
                                            timestamps,
                                            clean)
        if seg_info['MomentsData'].shape[0] > 0:
            segments_info[s] = seg_info
    return(segments_info)


def mergeSegment(seg, timestamps, clean):
    """
    ['Segment', 'Quarter', 'EventIds', 'PlayerIds', 'StartTime', 'EndTime', 'MomentsData']
    """
    
    q = seg.Quarter.copy().tolist()[0]
    eids = seg.EventId.copy().tolist()
    pids = seg.PlayerIds.copy().tolist()[0]
    start = seg.StartTime.copy().tolist()[0]
    end = seg.EndTime.copy().tolist()[-1]
    seg_moms = pandas.DataFrame()
    curr_indx = 0
    sm = None
    
    timestamps = set()

    for i,moment in enumerate(seg.MomentData):

       # if moment.game_clock[0] == numpy.max(moment.game_clock):
        
        stamps = zip(numpy.repeat(q, moment.shape[0]),
                     moment.game_clock)
        new_stamps = set(stamps).difference(timestamps)
        new_moms_indx = [row for (row, k) in zip(moment.index, stamps)\
                         if k in new_stamps]

        if new_moms_indx:
            new_moms = moment.ix[new_moms_indx].copy()
            new_moms.index = range(curr_indx, curr_indx + new_moms.shape[0])
            if i == 0:
                sm = new_moms.game_clock[0]
            curr_indx = curr_indx + new_moms.shape[0]
            seg_moms = pandas.concat([seg_moms, new_moms],
                                     axis = 0)

            # Update total set of (Quarter, Timestamp) pairs
            timestamps.update(new_stamps)
            
    if clean:
        seg_moms = cleanSegment(seg_moms)
        
    start = seg_moms.game_clock[0]
    end = seg_moms.game_clock.tolist()[-1]
    
    seg_info = {'Quarter' : q,
                'EventIds' : eids,
                'PlayerIds' : pids,
                'StartTime' : start,
                'StartMoments' : sm,
                'EndTime' : end,
                'MomentsData' : seg_moms,
                'NumMoments' : seg.shape[0]}
        
    return(seg_info, timestamps)


##################################################
#### Data Cleaning: Handles
##################################################


def cleanMoments(moments_info):
    """
    
    """
    keep = []
    # k_t = True ???
    for k in range(moments_info.shape[0]):
        p = moments_info.PlayerIds[k]
        m = moments_info.MomentData[k].copy()
        p, m, keep = cleanMoment(p, m, keep)
        moments_info.PlayerIds[k] = p
        moments_info.MomentData[k] = m
    moments_info = moments_info[keep]
    moments_info.index = range(moments_info.shape[0])
    return(moments_info)


def cleanSegments(segments_info):
    """
    :
    """
    for k, segment in segments_info.items():
        s = segment['MomentsData']
        s = cleanSegment(s)
        segment['MomentsData'] = s
        segments_info[k] = segment
    return(segments_info)


##################################################
#### Data Cleaning: Moments
##################################################


def cleanMoment(p, m, keep):
    """

    """
    k_t = True
    if len(p) != 11:
        m, p = removeFalsePlayers(m, p)
        if len(p) == 11:
            keep.append(True)
        else:
            k_t = False
            keep.append(False)
    else:
        k_t = True
        keep.append(True)
    if k_t and m.shape[0] % 11 != 0:
        m = removeMissedTimestamps(m, p)
    return(p, m, keep)


def removeFalsePlayers(md, pids, cutoff = 0.9):
    """
    Keep only players, ball occurring in at least 90% of the timestamps;
    """
    md = md.copy()
    fractions = numpy.zeros((len(pids),))
    
    for i, pid in enumerate(pids):
        fractions[i] = md[md.player_id == pid].shape[0]
    fractions = fractions / fractions.max()
    
    for k in list(numpy.where(fractions < cutoff)[0]):
        md = md[md.player_id != pids[k]]
        
    md.index = range(md.shape[0])
    pids = numpy.unique(md.player_id)
    return(md, pids)   


def removeMissedTimestamps(md, pids):
    """
    Remove timestamps that do not contain data for all 10 players and the ball
    """
    md = md.copy()
    n_players = len(pids)
    keep_list = []
    for t in numpy.unique(md.game_clock):
        if md[md.game_clock == t].shape[0] % n_players == 0:
            keep_list.append(t)
    bad_index = [k for (k,t) in zip(md.index, md.game_clock) if t not in keep_list]
    md = md.drop(bad_index)
    return(md)


##################################################
#### Data Cleaning: Segments
##################################################


def cleanSegment(s):
    """
    """
    s = removeClockStop(s)
    s = removeSpikes(s)
    s = removeRollbacks(s)
    return(s)


def removeClockStop(segment):
    """
    Remove "stopped clock" situations
    
    end_start_diff = [a - b for (a, b) in \
                  zip(game_info.ix[0:(game_info.shape[0]-2), 2], game_info.ix[1:(game_info.shape[0]-1), 1])]

    """
    ball_inds = range(0, segment.shape[0], 11)
    time_diff = segment.game_clock[ball_inds].diff() # If 0, current index is same as previous
    no_diff = numpy.where(time_diff == 0)[0]
    for nd in reversed(no_diff):
        targets = range((nd-1) * 11, nd * 11)
        segment = segment.drop(targets)
    segment.index = range(segment.shape[0])
    return(segment)


def removeSpikes(segment):
    """ """
    ball_inds = range(0, segment.shape[0], 11)
    time_diff = segment.game_clock[ball_inds].diff()
##    mtd = numpy.mean(time_diff))
##    stdt = numpy.std(time_diff))
    jumps = numpy.where(time_diff > 0.055)[0]
    drops = numpy.where(time_diff < -0.055)[0]
    for j in jumps:
        close_drops = numpy.where([f and g for (f,g) in \
                                   zip([d > j for d in drops],
                                       [d - j < 5 for d in drops])])[0]
        if len(close_drops) > 0:
            d = drops[close_drops[-1]]
##            print('Spike: %s to %s' % (j, d))
            segment = segment.drop(range(j*11, d*11))
            drops = drops[close_drops[-1]:]
    segment.index = range(segment.shape[0])
    return(segment)


def removeRollbacks(segment):
    """ """
    ball_inds = range(0, segment.shape[0], 11)
    time_diff = segment.game_clock[ball_inds].diff()
    jumps = list(numpy.where(time_diff > 0)[0])
    i = len(jumps) - 1
    while i > 0:
        ior = jumps[i]
        jumps.remove(ior)
        por = s.game_clock[ball_inds[ior]]
        t = -999
        ind = ior
        while t < por:
            ind -= 1
            t = segment.game_clock[ball_inds[ind]]
            if ind in jumps:
                jumps.remove(ind)
                i -= 1
        remove_range = range(ind * 11, ior * 11)
        segment = segment.drop(remove_range)
        i -= 1
    segment.index = range(segment.shape[0])
    return(segment)
