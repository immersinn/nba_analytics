
##import gameHelper
import momentsHelper
import eventsHelperNew as eventsHelper
import segmentsHelper

from dataFieldNames import *

reload(eventsHelper)


class NBAGameBasic:


    def __init__(self, teams,
                 player_ids, player_names, pid_name_lookup,
                 **kargs):
        self._set_attrs(teams,
                       player_ids, player_names, pid_name_lookup,
                       **kargs)


    def _set_attrs(self, teams,
                  player_ids, player_names, pid_name_lookup,
                  **kargs):
        self.teams = teams
        self.pids = player_ids
        self.pnames = player_names
        self.pid_name_lookup = pid_name_lookup


    @property
    def game_info_dict(self,):
        return({'teams' : self.teams,
                })


    @property
    def player_info_dict(self,):
        return({'player_ids' : self.pids,
                'player_names' : self.pnames,
                'pid_name_lookup' : self.pid_name_lookup,
                })



class NBAGameAnalysis(NBAGameBasic):


    def __init__(self, teams,
                 player_ids, player_names, pid_name_lookup,
                 moments_raw, pbp_raw,
                 **kargs):
        self._set_attrs(teams,
                       player_ids, player_names, pid_name_lookup,
                       moments_raw, pbp_raw,
                       **kargs)


    def _set_attrs(self, teams,
                  player_ids, player_names, pid_name_lookup,
                  moments_raw, pbp_raw,
                  **kargs):
        NBAGameBasics.set_attrs(teams,
                                player_ids, player_names, pid_name_lookup,
                                **kargs)
        self.moments_data = moments_raw
        self.events_data = pbp_raw


    def _init_data(self,):
        self._init_moment_class()
        self._init_events_class()
        self._init_segments_class()


    def _init_moment_class(self):
        self.moments = GameMoments(self.game_info_dict,
                                   self.player_info_dict,
                                   self.moments_raw)


    def _init_event_class(self):
        self.events = GameEvents(self.game_info_dict,
                                 self.player_info_dict,
                                 self.pbp_raw)


    def _init_segment_class(self):
        self.segments = GameSegments(self.game_info_dict,
                                     self.player_info_dict,
                                     self.moments_raw,
                                     self.pbp_raw)


    def extractTransitionGraph(self,):
        self._init_segment_class()
        self.segments.preprocess()
        self.segments.extractTransitionGraph()


    @property
    def transition_graph(self,):
        try:
            return(self.segments.transition_graph)
        except AttributeError:
            err_msg = "Transition Graph has not been extracted; run 'extractTransitionGraph' method"
            raise AttributeError, err_msg
                              
        

class GameSubpartBasic:

    def __getitem__(self, ITEM_TYPE, i):
        if ITEM_TYPE not in self.__dict__.keys():
            err_msg = 'No ' + ITEM_TYPE + ' currently associated'
            raise AttributeError, err_msg
        if i < self._count:
            return(self.__dict__[ITEM_TYPE][i])
        else:
            err_msg = 'Index out of bounds'
            raise KeyError, err_msg


    def __len__(self):
        if '_count' in self.__dict__.keys():
            return(self._count)
        else:
            return(0)


    def _init_attrs(self, **kargs):
        if 'game_info' in kargs.keys():
            self._set_game_info(kargs['game_info'])
        if 'player_info' in kargs.keys():
            self._set_player_info(kargs['player_info'])


    def _set_game_info(self, game_info):
        self._set_attrs(game_info)


    def _set_player_info(self, player_info):
        self._set_attrs(player_info)


    def _set_attrs(self, attrs):
        for k,v in attrs.items():
            setattr(self, k, v)


class GameSegments(GameSubpartBasic):


    def __init__(self, game_info, player_info, moments, pbp):
        
        self._init_attrs(game_info = game_info,
                         player_info = player_info)
        self._init_moments_events(game_info,
                                  player_info,
                                  moments, pbp)        
        self.__preprocess_flag = False


    def __getitem__(self, i):
        return(GameSubpartBasic.__getitem__(self, 'segments', i))


    def _init_moments_events(self, game_info, player_info, moments, pbp):

        self.moments = GameMoments(game_info,
                                   player_info,
                                   moments)
        self.events = GameEvents(game_info,
                                 player_info,
                                 pbp)

    
    def _align_moments_events(self,):
        self.ms_matches = segmentsHelper.matchEventsMoments(self.events,
                                                            self.moments)



    def _init_segments(self,):
        self.align_moments_events()
        self.game_segments = []
        for e,s in self.ms_matches:
            if e > -1 and s > -1:
                new = {}
                new_ = GameSegment(eid=e, events=self.events[e],
                                   mid=s, moment=self.moments[s])
            elif e == -1:
                new = GameSegment(eid=-1, events=None,
                                  mid=s, moment=self.moments[s])

            elif s == -1:
                new = GameSegment(eid=e, events=self.events[e],
                                  mid=-1, moment=None)
        new.preprocess()
        self.game_segments.append(new)


    def preprocess(self,):
        if not self.__preprocess_flag:
            self.moments.preprocess()
            self.events.preprocess()
            self._init_segments()
            self.__preprocess_flag = True
        else:
            pass


    def extractTransitionGraph(self,):
        all_transitions = []
        self.preprocess()
        for s in self.game_segments:
            s.extractTransitions()
            all_transitions.extend(s.transitions)
        self.transition_graph = all_transitions
        


class GameEvents(GameSubpartBasic):

    def __init__(self, pbp_info):

        self._init_attributes(pbp_info)
        self.pbp = eventsHelper.preprocessPbp(pbp_info['play_by_play'])
        self.__preprocess_flag = False
        
    
    def __getitem__(self, i):
        return(GameSubpartBasic.__getitem__(self, 'events', i))


    def _init_attributes(self, pbp_info):
        ha_dict = {'home' : pbp_info['game_stats']['HOME_TEAM_ID'][0],
                   'away' : pbp_info['game_stats']['VISITOR_TEAM_ID'][0]}
        ha_rev_dict = {pbp_info['game_stats']['HOME_TEAM_ID'][0] : 'home',
                       pbp_info['game_stats']['VISITOR_TEAM_ID'][0] : 'away'}
        team_info_dict = {ha_rev_dict[_id] : {'id' : _id,
                                              'name' : n, 'city' : c,
                                              'nickname' : nn, 'abb' : a} for \
                          (_id, n, c, nn, a) in zip(pbp_info['team_stats_adv']['TEAM_ID'],
                                                    pbp_info['team_stats_adv']['TEAM_NAME'],
                                                    pbp_info['team_stats_adv']['TEAM_CITY_NAME'],
                                                    pbp_info['team_stats_adv']['TEAM_NICKNAME'],
                                                    pbp_info['team_stats_adv']['TEAM_ABBREVIATION'])
                          }
        city_rev_lookup = {team_info_dict[k]['city'] : team_info_dict[k]['id'] \
                           for k in team_info_dict.keys()}
        player_info_list = [{'pid' : _id,
                            'name' : n,
                                   'city' : c,
                                   'team_id' : city_rev_lookup[c],
                                   'hORa' : ha_rev_dict[city_rev_lookup[c]]} for \
                            (_id, n, c) in zip(pbp_info['player_stats_adv']['PLAYER_ID'],
                                               pbp_info['player_stats_adv']['PLAYER_NAME'],
                                               pbp_info['player_stats_adv']['TEAM_CITY'])
                            ]
        for k in team_info_dict.keys():
            team_info_dict[k]['players'] = [p['pid'] for p in player_info_list if \
                                            p['team_id'] == team_info_dict[k]['id']]
        self.ha = ha_dict
        self.team_info = team_info_dict
        self.player_info = player_info_list
    

    def preprocess(self,):
        if not self.__preprocess_flag:
            self._determine_pbp_names()
            self._create_events()
            for e in self.events:
                e.preprocess()
            self.__preprocess_flag = True
##        self._players_on_court()
        else:
            pass


    def _determine_pbp_names(self,):
        self.player_info = eventsHelper.determinePlayerPBPNames(self.player_info,
                                                                self.pbp)


    def _players_on_court(self,):
        # attempt to determine which players on on
        # the court at a given time
        pass


    def _create_events(self,):
        self._events2event_list = \
                                eventsHelper.splitBySubsQuarters(self.pbp)
        self._num_events = len(self._events2event_list)
        self.events = [Events(self.pbp.ix[indxs].copy(),
##                              self.player_info_dict,
##                              self.players[indxs]) \
                              ) \
                       for indxs in self._events2event_list]
        self._count = len(self.events)




class GameMoments(GameSubpartBasic):

    def __init__(self,):
        pass


    def __getitem__(self, i):
        return(GameSubpartBasic.__getitem__(self, 'moments', i))


    def preprocess(self, data=None):
        # See 'Parse and Preproc Moments';
        # also, momentsHelper.py
        self._create_moments(data)


    def _create_moments(self, data):
        # segments_info = momentsHelper.preprocessSegments(moments)
        # remove duplicates
        # merge consec movements data
        # create Moment class for each
        pass






class Segment(object):


    def __init__(events_id, events,
                 moment_id, moment):
        self.eid = events_id
        self.events = events
        self.mid = moment_id
        self.moment = moment
        if events:
            self.quarter = events.quarter
        elif moment:
            self.quarter = moment.quarter


    def preprocess(self,):
        self.moment.preprocess()
        self.events.preprocess()


    def extractTransitions(self,):
        # The stuff that's currently in
        # "Match Ball Transitions to Posession Gaps"
        self.transitions = {} # or []??


class Moment(object):
    # All functionality that has been constructed for analyzing
    # the moment data (distances, plots, etc) goes in this class

    
    def preprocess(self,):
        pass


class Events:

    def __init__(self, pbp_segment):#, player_info, players,):
        # set the info passed
        # set Quarter
        # reduce list of players for each line item to a single list
        # other??
        self.pbp = pbp_segment
        self.__preprocess_flag = False


    def preprocess(self,):
        if not self.__preprocess_flag:
            self.__preprocess_flag = True
        else:
            pass


class Event(dict):

    """
    game clock, shot clock, quarter, player id / name, event type,
    event subtype, pbp sequence number, original pbp text
    """

    __slots__ = ()
    





        
        
