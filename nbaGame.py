
from . import momentsHelper
from . import eventsHelper
from . import segmentsHelper
from . import momentsCalculations
from .dataFieldNames import *

from importlib import reload
reload(eventsHelper)
reload(momentsHelper)
reload(segmentsHelper)


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
            raise AttributeError(err_msg)
                              
        

class GameSubpartBasic:


    def __getitem__(self, key, item_key=''):
        if not item_key:
            ITEM_NAME = self._SUB_TYPE_NAME
        else:
            ITEM_NAME = item_key
        if ITEM_NAME not in list(self.__dict__.keys()):
            err_msg = 'No ' + ITEM_NAME + ' currently associated'
            raise AttributeError(err_msg)
        return(self.__dict__[ITEM_NAME][key])


    def __len__(self):
        if '_count' in list(self.__dict__.keys()):
            return(self._count)
        elif hasattr(self, '_SUB_TYPE_NAME'):
            return(len(self.__dict__[self._SUB_TYPE_NAME]))
        else:
            return(0)


    def _init_attrs(self, **kargs):
        if 'game_info' in list(kargs.keys()):
            self._set_game_info(kargs['game_info'])
        if 'player_info' in list(kargs.keys()):
            self._set_player_info(kargs['player_info'])


    def _set_game_info(self, game_info):
        self._set_attrs(game_info)


    def _set_player_info(self, player_info):
        self._set_attrs(player_info)


    def _set_attrs(self, attrs):
        for k,v in list(attrs.items()):
            setattr(self, k, v)


class GameSegments(GameSubpartBasic):


    _SUB_TYPE_NAME = 'segments'


    def __init__(self, moments, pbp,
                 game_info, player_info):
        
##        self._init_attrs(game_info = game_info,
##                         player_info = player_info)
        
        if type(moments) == GameMoments:
            self._moments = moments
        else:
            pass
        if type(pbp) == GameEvents:
            self._events = pbp
        else:
            pass

##        self._moments = moments
##        self._events = pbp
            
##        self._init_moments_events(game_info,
##                                  player_info,
##                                  moments, pbp)
        self.__preprocess_flag = False


    def _init_moments_events(self, game_info, player_info, moments, pbp):

        self._moments = GameMoments(moments,
                                    game_info)
        self._events = GameEvents(pbp)

    
    def _align_moments_events(self,):
        self._matches = segmentsHelper.matchEventsMoments(self)


    def _init_segments(self,):
        self._align_moments_events()
        self.segments = []
        for i,(e,s) in enumerate(zip(list(self._matches.EventsId),
                                     list(self._matches.MomentId))):
            if e > -1 and s > -1:
                new = Segment(sid=i,
                              eid=e, events=self._events[e],
                              mid=s, moment=self._moments[s])
            elif e == -1:
                new = Segment(sid=i,
                              eid=-1, events=None,
                              mid=s, moment=self._moments[s])

            elif s == -1:
                new = Segment(sid=i,
                              eid=e, events=self._events[e],
                              mid=-1, moment=None)
            new.preprocess()
            self.segments.append(new)


    def preprocess(self,):
        if not self.__preprocess_flag:
            self._moments.preprocess()
            self._events.preprocess()
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


class GameMoments(GameSubpartBasic):


    _SUB_TYPE_NAME = 'moments'


    def __init__(self, movements_info, game_info, debug_mode=False):
        self._data = movements_info
        self._debug_mode = debug_mode
        # something with game_info


##    def __getitem__(self, i):
##        return(GameSubpartBasic.__getitem__(self, 'moments', i,
##                                            item_name = 'Moments'))


    def preprocess(self, ):
        self._create_moments()
        self._data = None
        self._pp_moments()


    def _create_moments(self,):
        mpp = momentsHelper.MomentsPreprocess(self._data,
                                              debug_mode = self._debug_mode)
        cols = mpp.meta.columns; cols = cols.insert(0, 'Index')
        self.moments = [Moment(mom, met) for (mom, met) in \
                        zip(list(mpp.moments.values()),
                            [{k : v for (k,v) in zip(cols, record)} \
                             for record in mpp.meta.to_records()])]
        self._count = len(self.moments)


    def _pp_moments(self,):
        for m in self.moments:
            m.preprocess()


class GameEvents(GameSubpartBasic):

    _SUB_TYPE_NAME = 'events'
    null_event = Event({'Event' : 'NONE',
                        'Player' : '',
                        'Team' : '',
                        'DESCRIPTION' : 'NullEvent',
                        'EVENTNUM' : int(),
                        'EVENTMSGTYPE' : -1,
                        'EVENTMSGACTIONTYPE' : int(),
                        'PERIOD' : int(),
                        'GAMECLOCK' : int(),
                        })
                        

    def __init__(self, pbp_info):
        self._init_attributes(pbp_info)
        self.pbp = eventsHelper.preprocessPbp(pbp_info['play_by_play'])
        self.__preprocess_flag = False
        
    
##    def __getitem__(self, i):
##        return(GameSubpartBasic.__getitem__(self, 'events', i,
##                                            item_name = 'Events'))


    def ix(self, i):
        return(GameSubpartBasic.__getitem__(self, i,
                                            item_key = '_events'))
##                                            item_name = 'Individual Events'))


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
                           for k in list(team_info_dict.keys())}
        player_info_list = [{'pid' : _id,
                            'name' : n,
                           'city' : c,
                           'team_id' : city_rev_lookup[c],
                           'hORa' : ha_rev_dict[city_rev_lookup[c]]} for \
                            (_id, n, c) in zip(pbp_info['player_stats_adv']['PLAYER_ID'],
                                               pbp_info['player_stats_adv']['PLAYER_NAME'],
                                               pbp_info['player_stats_adv']['TEAM_CITY'])
                            ]
        for k in list(team_info_dict.keys()):
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
##            _ = self.transitions
            self._create_events_groups()
            for e in self.events:
                e.preprocess()
##            self._pair_events_transitions()
            self.__preprocess_flag = True
            
        else:
            pass


    def _determine_pbp_names(self,):
        self.player_info = eventsHelper.determinePlayerPBPNames(self.player_info,
                                                                self.pbp)
        # FIX THIS!!!!!!
        # SHOULD DETERMINE WHO PLAYED BY BOX SCORE INFO / STATS, NOT HERE...
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
        self.events = [Events([self.ix(i) for i in el], j) \
                       for j,el in enumerate(self._events2event_list)]


    def _pair_events_transitions(self,):
        count = 0
        for e in self.events:
            if e.event_type in ['SUB', 'TIMEOUT']:
                e.transitions = []
            else:
                e.transitions = self.transitions[count]['TransitionsData']
                count += 1
                

    @property
    def transitions(self,):
        if '_transitions' not in self.__dict__.keys():
            print('Finding transitions for the first time...')
            ef = eventsHelper.TransitionsFinder(self._events,
                                                self.null_event)
            ef.getTransitions()
            self._transitions = ef.event_dict
        return(self._transitions)



class Segment(GameSubpartBasic):


    def __init__(self, sid,
                 eid, events,
                 mid, moment):
        self._ind = sid
        self._events = events
        self._moment = moment
        if self._events:
            self._tag = '_events'
        elif self._moment:
            self._tag = '_moment'


    def preprocess(self,):
        pass
##        self.moment.preprocess()
##        self.events.preprocess()


    def extractTransitions(self,):
        # The stuff that's currently in
        # "Match Ball Transitions to Posession Gaps"
        self.transitions = {} # or []??


    @property
    def ind(self,):
        return(self._ind)


    @property
    def period(self,):
        return(self.__dict__[self._tag].period)


    @property
    def start(self,):
        return(self.__dict__[self._tag].start)


    @property
    def end(self,):
        return(self.__dict__[self._tag].end)


    @property
    def players(self,):
        return(self.__dict__[self._tag].players)


    @property
    def eventsId(self,):
        if self._events:
            return(self._events.ind)
        else:
            return(None)

    
    @property
    def momentId(self,):
        if self._moment:
            return self._moment.ind
        else:
            return(None)
    


class Moment(GameSubpartBasic):
    # All functionality that has been constructed for analyzing
    # the moment data (distances, plots, etc) goes in this class

    def __init__(self, moment, meta):
        self._data = moment
        self._meta = meta
        self._count = self._data.shape[0]


    def preprocess(self, ):
        _ = self.ballTransitions


    @property
    def ballTransitions(self,):
        if '_transitions' not in self.__dict__.keys():
            self._transitions = momentsCalculations.\
                                determineBallTransitions(self._data,
                                                         self.players,
                                                         self.ballPosessions)
        return(self._transitions)
                                                                

    @property
    def ballPosessions(self,):
        if '_ball_poss' not in self.__dict__.keys():
            self._ball_poss = momentsCalculations.\
                              determineBallPosessions(self._data,
                                                      self.players)
        return(self._ball_poss)


    @property
    def period(self,):
        return(self._meta['Period'])


    @property
    def ind(self,):
        return(self._meta['MomentId'])


    @property
    def start(self,):
##        return(self.meta['StartTime'])
        return(self._meta['DataStartTime'])


    @property
    def end(self,):
##        return(self.meta['EndTime'])
        return(self._meta['DataEndTime'])


    @property
    def players(self,):
        return(list(self._meta['PlayerIds']))


    @property
    def events(self,):
        return(self._meta['EventIds'])


    def player2playerDist(self, pid1, pid2):
        err_msg = 'Player does not exist in data: '
        if pid1 not in self.players:
            err_msg += str(pid1)
            raise AttributeError(err_msg)
        if pid2 not in self.players:
            err_msg += str(pid2)
            raise AttributeError(err_msg)

        return(momentsCalculations.\
               calcP2PDist(self._data, pid1, pid2))


class Events(GameSubpartBasic):


    _SUB_TYPE_NAME = 'events'
    null_event = Event({'Event' : 'NONE',
                        'Player' : '',
                        'Team' : '',
                        'DESCRIPTION' : 'NullEvent',
                        'EVENTNUM' : int(),
                        'EVENTMSGTYPE' : -1,
                        'EVENTMSGACTIONTYPE' : int(),
                        'PERIOD' : int(),
                        'GAMECLOCK' : int(),
                        })


    def __init__(self, events, ind):#, player_info, players,):
        # set the info passed
        # reduce list of players for each line item to a single list
        # set players
        # other??
        self.events = events
        self._ind = ind
        self._count = len(events)
        self.__preprocess_flag = False


    def __getitem__(self, i):
        return(GameSubpartBasic.__getitem__(self, i))


    def __str__(self,):
        return(str(self.events))


    def _determine_ball_transitions(self,):
        pass


    def _determine_events_type(self,):
        if self.events[0]['Event'] in ['SUB_IN', 'SUB_OUT']:
            self._event_type = 'SUB'
        elif self.events[0]['Event'] == 'TIMEOUT' \
             and len(self.events) == 1:
            self._event_type = 'TIMEOUT'
        else:
            self._event_type = 'REGULAR_PLAY'       


    def preprocess(self,):
        self._determine_events_type()
        _ = self.transitions
##        if not self.__preprocess_flag:
##            for e in self.events:
##                e.preprocess()
##            self.__preprocess_flag = True
##        else:
##            pass
    

    @property
    def period(self,):
        return(self[0]['PERIOD'])


    @property
    def start(self,):
        return(self[0]['GAMECLOCK'])


    @property
    def end(self,):
        return(self[-1]['GAMECLOCK'])


    @property
    def players(self,):
        return(self[0]['PlayersOnCourt'])


    @property
    def ind(self,):
        return(self._ind)


    @property
    def event_type(self,):
        return(self._event_type)


    @property
    def transitions(self,):
        if '_transitions' not in self.__dict__.keys():
            if self.event_type == 'SUB':
                self._transitions = {}
            else:
##                print('Finding transitions for the first time...')
                ef = eventsHelper.TransitionsFinder(self.events,
                                                    self.null_event)
                ef.getTransitions()
                if len(ef.event_dict) == 1:
                    self._transitions = ef.event_dict[0]
                else:
                    self._transitions = ef.event_dict
        return(self._transitions)



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
    
