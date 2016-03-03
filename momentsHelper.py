
import numpy
import pandas


MOMENTS_HEADERS = ['team_id', 'player_id',
                   'game_clock', 'x_loc', 'y_loc', 'radius',
                   'timestamp', 'shot_clock',
                   'moment', ]

MOMENTS_ATTRS = ('event_id', 'quarter',
                 'game_clock_start', 'game_clock_end',
                 'shot_clock_start', 'shot_clock_end',)

MOM_ATTRS_COLS = ('EventId', 'Period',
                  'StartTime', 'EndTime',
                  'ShotStart', 'ShotEnd',)

MOM_ATTR_LOOK = {k : v for (k,v) in zip(MOMENTS_ATTRS, MOM_ATTRS_COLS)}

META_NEW_ATTRS = ['MomentId',
                  'StartTime', 'EndTime',
                  'DataStartTime', 'DataEndTime',
                  'ShotStart', 'ShotEnd',
                  'Period',
                  'EventIds',
                  'PlayerIds',]



##################################################
#### Build, Filter, Clean Moments:
#### Full Moments Preprocessing
##################################################


class MomentsPreprocess:


    def __init__(self, game_moments,
                 segment_criteria = 'Player',
                 debug_mode = False):
        self.sc = segment_criteria
        self.raw = game_moments._data
        self.team_info = game_moments.team_info
        self.orderMomentsByTimestamp()
        if not debug_mode:
            self.buildMeta()
            self.buildMoments()
            self.updateMeta()


    def orderMomentsByTimestamp(self,):
        first_timestamps = [m['timestamp'][0] for m in self.raw]
        sort_indx = numpy.argsort(first_timestamps)
        self.raw = [self.raw[i] for i in sort_indx]
        for i,m in enumerate(self.raw):
            m['event_id_orig'] = m['event_id']
            m['event_id'] = int2evid(i)


    def buildMeta(self,):
        self.initMetaInfo()
        self.filterMetaInfo()
        

    def initMetaInfo(self,):
        meta_info = pandas.DataFrame(data = {k : [self.raw[i][k] \
                                                  for i in range(len(self.raw))] \
                                             for k in MOMENTS_ATTRS})
        meta_info.sort_index(by='event_id', inplace=True)
        meta_info.columns = [MOM_ATTR_LOOK[c] for c in meta_info.columns]
        self.meta = meta_info


    def filterMetaInfo(self,):
        # Filter out moments that are encompassed by other moments
        # (diff for entry 0 is 'NaN', so it stays)
        keep = [s !=0 or e != 0 for (s,e) in zip(self.meta.StartTime.diff(),
                                                 self.meta.EndTime.diff())]
        self.meta = self.meta.ix[keep]#.copy()
        
        # Remove moments where no time ellapses
        keep = [s != e for (s,e) in zip(self.meta.StartTime,
                                        self.meta.EndTime)]
        self.meta = self.meta.ix[keep]#.copy()

        # Reindex data
        self.meta.index = list(range(self.meta.shape[0]))


    def buildMoments(self,):
        self.initMoments()
        self.momentsFromParts()


    def initMoments(self,):
        moments = {}
        eids = set(self.meta.EventId)
        e = []; p = []
        for m in self.raw:
            if m['event_id'] in eids:
                mom = initSubMoment(m)
                if mom.shape != (0,0):
                    e.append(m['event_id'])
                    p.append(sorted(pandas.unique(mom.player_id)))
                    moments[m['event_id']] = mom

        self.meta = pandas.merge(self.meta,
                                 pandas.DataFrame(data = {'EventId' : e,
                                                          'PlayerIds' : p}))
        self.moments = moments


    def momentsFromParts(self,):
        self.findMomentParts()
        self.mergeMomentParts()


    def findMomentParts(self,):
        self.samePeriod()
        self.samePlayers()
        if self.sc == 'TimePlayer':
            self.overlapTimes()
            seg_flag = [a & b & c for (a, b, c) in \
                              zip(self.meta.Overlap.tolist(),
                                  self.meta.SamePlayers.tolist(),
                                  self.meta.SamePeriod.tolist())]
        elif self.sc== 'Player':
            seg_flag = [a & b for (a, b) in \
                        zip(self.meta.SamePlayers.tolist(),
                            self.meta.SamePeriod.tolist())]

        seg_count = 0; segments = [0];
        for i in seg_flag[1:]:
            if not i:
                seg_count += 1
            segments.append(seg_count)

        self.meta = self.meta.join(\
            pandas.DataFrame(data = {'Segment' : segments}))


    def mergeMomentParts(self,):
        meta = []
        moments = {}
        for s in pandas.unique(self.meta.Segment):
            met = self.meta[self.meta.Segment==s]
            eids = met.EventId.tolist()
            met = mergeMeta(s, met)
            mom = mergeAndCleanParts({k : m for (k,m) in list(self.moments.items()) \
                                      if k in eids})
            if mom.shape[0] > 0:
                met['DataStartTime'] = max(mom.game_clock)
                met['DataEndTime'] = min(mom.game_clock)
                meta.append(met)
                moments[s] = mom

        self.meta = pandas.DataFrame({k : m[k] \
                                      for k in META_NEW_ATTRS} \
                                     for m in meta)
        self.moments = moments


    def samePeriod(self,):
        same_period = [self.meta.Period[i] == \
                       self.meta.Period[i-1] \
                       for i in range(1, self.meta.shape[0])]
        same_period.insert(0, True)
        self.meta = self.meta.join(\
            pandas.DataFrame(data = {'SamePeriod' : same_period}))


    def samePlayers(self,):
        same_players = [list(sorted(self.meta.PlayerIds[i])) == \
                        list(sorted(self.meta.PlayerIds[i-1])) \
                        for i in range(1, self.meta.shape[0])]
        same_players.insert(0, True)
        self.meta = self.meta.join(\
            pandas.DataFrame(data = {'SamePlayers' : same_players}))


    def overlapTimes(self,):
        overlap = [(a - b) < 0 for (a, b) in \
                   zip(self.meta.EndTime.tolist(),
                       self.meta.StartTime.tolist())]
        overlap.insert(0, True)
        self.meta = self.meta.join(\
            pandas.DataFrame(data = {'Overlap' : overlap}))


    def updateMeta(self,):
        """
        'PlayerIds'
        """
        pids = self.meta.PlayerIds.tolist()
        hpids = []; vpids = [];
        home = set(self.team_info['home']['players'])
        away = set(self.team_info['away']['players'])
        for p in pids:
            hpids.append(list(home.intersection(p)))
            vpids.append(list(away.intersection(p)))
        self.meta = self.meta.join(\
            pandas.DataFrame(data = {'HomePlayers' : hpids,
                                     'AwayPlayers' : vpids}))
        


###################################


def int2evid(val):
    if val < 10:
        return('00' + str(val))
    elif val < 100:
        return('0' + str(val))
    else:
        return(str(val))


def initSubMoment(m):

    mdf = pandas.DataFrame(data = {k : m[k] for k in MOMENTS_HEADERS})
    pids = pandas.unique(mdf.player_id)

    if len(pids) != 11:
        mdf = removeFalsePlayers(mdf)
    if len(pandas.unique(mdf.player_id)) == 11 and \
       mdf.shape[0] % 11 != 0:
        mdf = removeMissedTimestamps(mdf)
    if len(pandas.unique(mdf.player_id)) == 11 and \
       -1 in pandas.unique(mdf.player_id):
        return(mdf)
    else:
        return(pandas.DataFrame())


def removeFalsePlayers(mdf, cutoff = 0.9):
    
    pids = pandas.unique(mdf.player_id)
    fractions = pandas.Series([mdf[mdf.player_id == p].shape[0] for p in pids])
    fractions /= fractions.max()

    for i,f in enumerate(fractions):
        if f < cutoff:
            mdf.drop(mdf.index[mdf.player_id==pids[i]], inplace=True)

    mdf.index = list(range(mdf.shape[0]))

    return(mdf)


def removeMissedTimestamps(mdf):
    """
    Remove timestamps that do not contain data for all 10 players and the ball
    """
    n_players = len(pandas.unique(mdf.player_id))
    for t in pandas.unique(mdf.timestamp):
        if mdf[mdf.timestamp == t].shape[0] != n_players:
            mdf.drop(mdf.index[mdf.timestamp == t], inplace=True)
    return(mdf)



def mergeMeta(s, metas):
    return({'MomentId' : s,
            'StartTime' : metas.StartTime.tolist()[0],
            'EndTime' : metas.EndTime.tolist()[-1],
            'ShotStart' : metas.ShotStart.tolist()[0],
            'ShotEnd' : metas.ShotEnd.tolist()[-1],
            'PlayerIds' : metas.PlayerIds.tolist()[0],
            'EventIds' : metas.EventId.tolist(),
            'Period' : metas.Period.tolist()[0],
            })


def mergeAndCleanParts(mom_dict):
    moment = mergeParts(mom_dict)
    moment = cleanMoment(moment)
    return(moment)


def mergeParts(mom_dict):
   
    merged = pandas.DataFrame()
    timestamps = set()
    curr_indx = 0

    for k in sorted(mom_dict.keys()):
        
        moment = mom_dict[k]
        stamps = moment.game_clock
        new_stamps = set(stamps).difference(timestamps)
        new_moms_indx = [row for (row, k) in zip(moment.index, stamps)\
                         if k in new_stamps]

        if new_moms_indx:
            new_moms = moment.ix[new_moms_indx].copy()
            new_moms.index = list(range(curr_indx, curr_indx + new_moms.shape[0]))
            merged = pandas.concat([merged, new_moms], axis = 0)
            timestamps.update(new_stamps)
            curr_indx = curr_indx + new_moms.shape[0]

    merged.index = list(range(merged.shape[0]))
##    merged.sort_index(by = 'timestamp', inplace = True)

    return(merged)


def cleanMoment(m):
    m = removeClockStop(m)
    m = removeSpikes(m)
    m = removeRollbacks(m)
    return(m)


def removeClockStop(segment):
    """
    Remove "stopped clock" situations
    
    end_start_diff = [a - b for (a, b) in \
                  zip(game_info.ix[0:(game_info.shape[0]-2), 2], game_info.ix[1:(game_info.shape[0]-1), 1])]

    """
    ball_inds = list(range(0, segment.shape[0], 11))
    time_diff = segment.game_clock[ball_inds].diff() # If 0, current index is same as previous
    no_diff = numpy.where(time_diff == 0)[0]
    for nd in reversed(no_diff):
        targets = list(range((nd-1) * 11, nd * 11))
        segment = segment.drop(targets)
    segment.index = list(range(segment.shape[0]))
    return(segment)


def removeSpikes(segment):
    """ """
    ball_inds = list(range(0, segment.shape[0], 11))
    time_diff = segment.game_clock[ball_inds].diff()
    jumps = numpy.where(time_diff > 0.055)[0]
    drops = numpy.where(time_diff < -0.055)[0]
    removed_inds = set()
    for j in jumps:
        if j not in removed_inds:
            close_drops = numpy.where([f and g for (f,g) in \
                                       zip([d > j for d in drops],
                                           [d - j < 5 for d in drops])])[0]
        else:
            close_drops = []
        if len(close_drops) > 0:
            d = drops[close_drops[-1]]
            removed_inds.update(set(range(j, d)))
            segment = segment.drop(list(range(j*11, d*11)))
            drops = drops[close_drops[-1]:]
    segment.index = list(range(segment.shape[0]))
    return(segment)


def removeRollbacks(segment):
    """ """
    ball_inds = list(range(0, segment.shape[0], 11))
    time_diff = segment.game_clock[ball_inds].diff()
    jumps = list(numpy.where(time_diff > 0)[0])
    i = len(jumps) - 1
    while i > 0:
        ior = jumps[i]
        jumps.remove(ior)
        por = segment.game_clock[ball_inds[ior]]
        t = -999
        ind = ior
        while t < por:
            ind -= 1
            t = segment.game_clock[ball_inds[ind]]
            if ind in jumps:
                jumps.remove(ind)
                i -= 1
        remove_range = list(range(ind * 11, ior * 11))
        segment = segment.drop(remove_range)
        i -= 1
    segment.index = list(range(segment.shape[0]))
    return(segment)

