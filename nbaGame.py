
##import gameHelper
import momentsHelper
import eventsHelper
import segmentsHelper

from dataFieldNames import *

reload(momentsHelper)


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

    def __getitem__(self, ITEM_TYPE, key, item_name = ''):
        if not item_name:
            item_name = ITEM_TYPE
        if ITEM_TYPE not in self.__dict__.keys():
            err_msg = 'No ' + ITEM_TYPE + ' currently associated'
            raise AttributeError, err_msg
        return(self.__dict__[ITEM_TYPE][key])


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
        return(GameSubpartBasic.__getitem__(self, 'events', i,
                                            item_name = 'Events'))


    def ix(self, i):
        return(GameSubpartBasic.__getitem__(self, '_events', i,
                                            item_name = 'Individual Events'))


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
            team_info_dict[k]['starters'] = team_info_dict[k]['players'][:5]
            
        self.ha = ha_dict
        self.team_info = team_info_dict
        self.player_info = player_info_list
    

    def preprocess(self,):
        if not self.__preprocess_flag:
            self._determine_pbp_names()
            self._create_events_indi()
            self._determine_periods()
            self._players_on_court()
            self._create_events_groups()
            for e in self.events:
                e.preprocess()
            self.__preprocess_flag = True
            
        else:
            pass


    def getTransitions(self,):
        ef = eventsHelper.EventsFinder(self._events)
        ef.getEvents()
        self.transition_dict = ef.event_dict


    def _determine_pbp_names(self,):
        self.player_info = eventsHelper.determinePlayerPBPNames(self.player_info,
                                                                self.pbp)
        # FIX THIS!!!!!!
        # SHOULD DETERMINE BY BOX SCORE INFO / STATS, NOT HERE...
        for p in self.player_info:
            if not p['pbp_name']:
                p['played_game'] = False
            else:
                p['played_game'] = True
        self.id2name = {p['pid'] : p['pbp_name'] for \
                        p in self.player_info if p['played_game']}
        self.name2id = {p['pbp_name'] : p['pid'] for \
                        p in self.player_info if p['played_game']}


    def _determine_periods(self,):
        periods = sorted(list(set([ev['PERIOD'] for ev in self._events])))
        self.periods = periods


    def _players_on_court(self,):
        # Edits individual events in-place,
        # so no need to return anything
        eventsHelper.playersForEventsGame(self)


    def _create_events_indi(self,):
        
        self._events = [Event(ev) for \
                        ev in eventsHelper.events2Entries(self.pbp)]
        
        for e in self._events:
            if e['Event'] in ['TO-UNKN', 'FOUL-UNKN']:
                # Two types of events for which we don't know
                # what the description looks like well enough
                # to "dead-reckon" pull the name
                team = e['Team']
                p_lnames = [p['last_name'] for \
                            p in self.player_info \
                            if p['pid'] in self.team_info[team]['players']]
                p_pbp_names = [p['pbp_name'] for \
                            p in self.player_info \
                            if p['pid'] in self.team_info[team]['players']]
                e['Player'] = eventsHelper.\
                              playerNameFromDescrip(e['DESCRIPTION'],
                                                    p_lnames,
                                                    p_pbp_names)
                                                    
            try:
                e['pid'] = self.name2id[e['Player']]
            except KeyError:
                e['pid'] = None
                
        self._num_events = len(self._events)
        for i in range(self._num_events):
            self.ix(i)['Index'] = i


    def _create_events_groups(self,):

        self._events2event_list  = \
                      eventsHelper.splitEventsBySubsQuarters(self._events)
        self._count = len(self._events2event_list)
        self.events = [Events([self.ix(i) for \
                               i in el]) for\
                       el in self._events2event_list]



class GameMoments(GameSubpartBasic):


    def __init__(self, movements_info, game_info):
        self._data = movements_info
        # something with game_info


    def __getitem__(self, i):
        return(GameSubpartBasic.__getitem__(self, 'moments', i,
                                            item_name = 'Moments'))


    def preprocess(self, ):
        # See 'Parse and Preproc Moments';
        # also, momentsHelper.py
        self._create_moments()
        self._data = None


    def _create_moments(self,):
        # segments_info = momentsHelper.preprocessSegments(moments)
        # remove duplicates
        # merge consec movements data
        # create Moment class for each
        self._mpp = momentsHelper.MomentsPreprocess(self._data)

    """
    Is it strange that the MomentsPreprocess instance still
    "owns" this data?
    """

    @property
    def meta(self,):
        return(self._mpp.meta)

    @property
    def moments(self,):
        return(self._mpp.moments)


class Segment(GameSubpartBasic):


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


class Moment(GameSubpartBasic):
    # All functionality that has been constructed for analyzing
    # the moment data (distances, plots, etc) goes in this class

    def preprocess(self,):
        pass


class Events(GameSubpartBasic):


    def __init__(self, events):#, player_info, players,):
        # set the info passed
        # reduce list of players for each line item to a single list
        # set players
        # other??
        self.events = events
        self._count = len(events)
        self.__preprocess_flag = False


    def __getitem__(self, i):
        return(GameSubpartBasic.__getitem__(self, 'events', i))


    def __str__(self,):
        return(str(self.events))


    def _determine_ball_transitions(self,):
        pass


    @property
    def start(self,):
        return(self[0]['GAMECLOCK'])


    @property
    def end(self,):
        return(self[-1]['GAMECLOCK'])


    @property
    def period(self,):
        return(self[0]['PERIOD'])


    @property
    def players(self,):
        return(self[0]['Players'])


    def preprocess(self,):
        pass
##        if not self.__preprocess_flag:
##            for e in self.events:
##                e.preprocess()
##            self.__preprocess_flag = True
##        else:
##            pass


class Event(dict):

    """
    game clock, shot clock, quarter, player id / name, event type,
    event subtype, pbp sequence number, original pbp text
    """

    __slots__ = ()


    def preprocess(self,):
        pass


    @property
    def DESCRIPTION(self,):
        return(self['DESCRIPTION'])

    @property
    def Event(self,):
        return(self['Event'])

    @property
    def EVENTMSGACTIONTYPE(self,):
        return(self['EVENTMSGACTIONTYPE'])

    @property
    def EVENTMSGTYPE(self,):
        return(self['EVENTMSGTYPE'])

    @property
    def EVENTNUM(self,):
        return(self['EVENTNUM'])

    @property
    def GAMECLOCK(self,):
        return(self['GAMECLOCK'])

    @property
    def PERIOD(self,):
        return(self['PERIOD'])

    @property
    def pid(self,):
        return(self['pid'])
    
    @property
    def Player(self,):
        return(self['Player'])

    @property
    def PlayersOnCourt(self,):
        return(self['PlayersOnCourt'])

    @property
    def Team(self,):
        return(self['Team'])
    

