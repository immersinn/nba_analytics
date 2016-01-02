
import pandas

from nba_analytics import fileHelper
from nba_analytics import momentsHelper
from nba_analytics import pbpHelper
from nba_analytics import pbpParser


class ParsedGamePrep:

    def __init__(self,):
        self.defaultFileLoad()
        self.defaultGameInfo()
        self.preprocSegments()
        self.preprocEvents()
        self.mergeContent()


    def defaultFileLoad(self,):
        moments, pbp = fileHelper.grabGameFromLoad()
        self.moments = moments
        
        self.pi = pbp['player_info']
        # How can this be automated from game data?
        # Should be able to pull from pbp
        self.team_names = ['Clippers', 'Spurs', 'CLIPPERS', 'SPURS']

        self.pbp = preprocessPbp(pbp)


    def defaultGameInfo(self,):
        # Info about players, game
        # Moved some into 'defaultFileLoad', since it will likely
        # be initiated from PBP data
        
        self.name2id = {name : id_ for (name, id_) in zip(self.pi['PLAYER_NAME'],
                                                 self.pi['PLAYER_ID'])}
        self.pbp_names = [n.split()[1] for n in self.pi['PLAYER_NAME']]
        self.pbp2id = {name : id_ for (name, id_) in zip(self.pbp_names,
                                                self.pi['PLAYER_ID'])}


    def pairSegEve(self,):
        matches = matchSegmentsEvents(self.segments,
                                      self.events)
        merged_data = mergeSegmentsEvents(matches,
                                          self.events,
                                          self.segments)
        self.paired_seg_eve = merged_data


    def preprocSegments(self,):
        self.segments = momentsHelper.preprocessSegments(self.moments)


    def preprocEvents(self,):
        self.esf = pbpParser.EventsFinder(self.pbp,
                                          self.pbp_names,
                                          self.team_names,
                                        self.pbp2id)
        self.esf.getEvents()
        self.events = self.esf.event_dict


    def mergeContent(self,):
        self.content = mergeSegmentsEvents(self.events,
                                           self.segments)



def preprocessPbp(pbp):
    pbp = pbpHelper.pbpDict2Df(pbp)
    pbp = addIndex(pbp)
    pbp = addGameClock(pbp)
    return(pbp)


def addIndex(pbp):
    ind = pandas.DataFrame(data = range(pbp.shape[0]),
                           columns = ['Index'])
    pbp = pbp.join(ind)
    return(pbp)


def addGameClock(pbp):
    gc = [pbpParser.time2Gc(t) for t in pbp.PCTIMESTRING]
    gc = pandas.DataFrame(data = zip(pbp.Index, gc),
                          columns = ['Index', 'game_clock'])
    pbp = pbp.merge(gc)
    return(pbp)


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

    matches = matchEventsMoments(events, moments)
    paired_eve_mom = []

    for e,s in matches:
        
        if e > -1 and s > -1:
            new = {'eid' : e, 'event' : events[e],
                   'mid' : s, 'moment' : moments[s],
                   'Quarter' : events[e]['Quarter']}
        elif e == -1:
            new = {'eid' : -1, 'event' : None,
                   'mid' : s, 'moment' : moments[s],
                   'Quarter' : moments[s]['Quarter']}
        elif s == -1:
            new = {'eid' : e, 'event' : events[e],
                   'mid' : -1, 'moment' : None,
                   'Quarter' : events[e]['Quarter']}
            
        paired_eve_mom.append(new)

    return(paired_eve_mom)


def main():
    pgp = ParsedGamePrep()
    return(pgp)
