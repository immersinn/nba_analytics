
from . import momentsHelper
from . import eventsHelper
from . import segmentsHelper
from . import momentsCalculations
from .dataFieldNames import *

##from importlib import reload
##reload(eventsHelper)
##reload(momentsHelper)
##reload(momentsCalculations)
##reload(segmentsHelper)



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


class EventBallTransition(dict):

    """
    Should contain all info related to a ball transition
    Should allow for callable attributes, like Event Class
    """

    __slots__ = ()


    def preprocess(self,):
        pass

    @property
    def ind(self,):
        return(self['ind'])

    @property
    def Period(self,):
        return(self['Period'])

    @property
    def GameClock(self,):
        # Event Trans Only to start
        return(self['GameClock'])

    @property
    def FromPlayer(self,):
        return(self['FromPlayer'])

    @property
    def ToPlayer(self,):
        return(self['ToPlayer'])

    @property
    def TransitionType(self,):
        # Event Trans Only to start
        return(self['TransitionType'])

    @property
    def TransSubType(self,):
        # Event Trans Only to start
        return(self['TransSubType'])


class MomentBallTransition(dict):

    """
    Should contain all info related to a ball transition
    Should allow for callable attributes, like Event Class
    """

    __slots__ = ()



    def preprocess(self,):
        pass

    @property
    def ind(self,):
        return(self['ind'])

    @property
    def StartIndx(self,):
        # Moment Trans Only to start
        return(self['StartIndx'])

    @property
    def EndIndx(self,):
        # Moment Trans Only to start
        return(self['EndIndx'])

    @property
    def Period(self,):
        return(self['Period'])

    @property
    def StartGameClock(self,):
        # Moment Trans Only to start
        return(self['StartGameClock'])

    @property
    def EndGameClock(self,):
        # Moment Trans Only to start
        return(self['EndGameClock'])

    @property
    def FromPlayer(self,):
        return(self['FromPlayer'])

    @property
    def ToPlayer(self,):
        return(self['ToPlayer'])


class BallTransition(MomentBallTransition, EventBallTransition):

    """
    Should contain all info related to a ball transition
    Should allow for callable attributes, like Event Class
    """

    __slots__ = ()


    def preprocess(self,):
        pass

    @property
    def eventId(self,):
        return(self['eventId'])

    @property
    def momentId(self,):
        return(self['momentId'])

    

class NBAGameBasic:


    def __init__(self, teams,
                 player_ids, player_names, pid_name_lookup,
                 **kargs):
        self._setAttrs(teams,
                       player_ids, player_names, pid_name_lookup,
                       **kargs)


    def _setAttrs(self, teams,
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


    def _setAttrs(self, teams,
                  player_ids, player_names, pid_name_lookup,
                  moments_raw, pbp_raw,
                  **kargs):
        NBAGameBasics.set_attrs(teams,
                                player_ids, player_names, pid_name_lookup,
                                **kargs)
        self.moments_data = moments_raw
        self.events_data = pbp_raw


    def _initData(self,):
        self._init_moment_class()
        self._init_events_class()
        self._init_segments_class()


    def _initMomentClass(self):
        self.moments = GameMoments(self.game_info_dict,
                                   self.player_info_dict,
                                   self.moments_raw)


    def _initEventClass(self):
        self.events = GameEvents(self.game_info_dict,
                                 self.player_info_dict,
                                 self.pbp_raw)


    def _initSegmentClass(self):
        self.segments = GameSegments(self.game_info_dict,
                                     self.player_info_dict,
                                     self.moments_raw,
                                     self.pbp_raw)


    def extractTransitionGraph(self,):
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


class GameSubpartFull(GameSubpartBasic):


    def _initAttrs(self, **kargs):
        if 'game_info' in list(kargs.keys()):
            self._setGameInfo(kargs['game_info'])
        if 'player_info' in list(kargs.keys()):
            self._setPlayerInfo(kargs['player_info'])


    def _setGameInfo(self, game_info):
        self._setAttrs(game_info)


    def _setPlayerInfo(self, player_info):
        self._setAttrs(player_info)


    def _setAttrs(self, attrs):
        for k,v in list(attrs.items()):
            setattr(self, k, v)


    def _initGameAttributes(self, game_info):
        ha_dict = {'home' : int(game_info['game_stats']['HOME_TEAM_ID'][0]),
                   'away' : int(game_info['game_stats']['VISITOR_TEAM_ID'][0])}
        ha_rev_dict = {game_info['game_stats']['HOME_TEAM_ID'][0] : 'home',
                       game_info['game_stats']['VISITOR_TEAM_ID'][0] : 'away'}
        team_info_dict = {ha_rev_dict[_id] : {'id' : _id,
                                              'name' : n, 'city' : c,
                                              'nickname' : nn, 'abb' : a} for \
                          (_id, n, c, nn, a) in zip(game_info['team_stats_adv']['TEAM_ID'],
                                                    game_info['team_stats_adv']['TEAM_NAME'],
                                                    game_info['team_stats_adv']['TEAM_CITY_NAME'],
                                                    game_info['team_stats_adv']['TEAM_NICKNAME'],
                                                    game_info['team_stats_adv']['TEAM_ABBREVIATION'])
                          }
        city_rev_lookup = {team_info_dict[k]['city'] : team_info_dict[k]['id'] \
                           for k in list(team_info_dict.keys())}
        player_info_list = [{'pid' : _id,
                            'name' : n,
                           'city' : c,
                           'team_id' : city_rev_lookup[c],
                           'hORa' : ha_rev_dict[city_rev_lookup[c]]} for \
                            (_id, n, c) in zip(game_info['player_stats_adv']['PLAYER_ID'],
                                               game_info['player_stats_adv']['PLAYER_NAME'],
                                               game_info['player_stats_adv']['TEAM_CITY'])
                            ]
        for k in list(team_info_dict.keys()):
            team_info_dict[k]['players'] = [p['pid'] for p in player_info_list if \
                                            p['team_id'] == team_info_dict[k]['id']]
            team_info_dict[k]['starters'] = team_info_dict[k]['players'][:5]
            
        self.gid = game_info['game_id']
        self.ha = ha_dict
        self.team_info = team_info_dict
        self.player_info = player_info_list


class GameSegments(GameSubpartFull):


    _SUB_TYPE_NAME = 'segments'


    def __init__(self, game_info,
                 moments, pbp):

        self._initGameAttributes(game_info)
        
        if type(moments) == GameMoments:
            self._moments = moments
        else:
            self._moments = GameMoments(game_info, moments)
        if type(pbp) == GameEvents:
            self._events = pbp
        else:
            self._events = GameEvents(game_info, pbp)

        self.__preprocess_flag = False


    def _initMomentsEvents(self, game_info, moments, pbp):

        self._moments = GameMoments(game_info, moments)
        self._events = GameEvents(game_info, pbp)

    
    def _alignMomentsEvents(self,):
        self._matches = segmentsHelper.matchEventsMoments(self)


    def _initSegments(self,):
        self._alignMomentsEvents()
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
            print('Preprocessing moments...')
            self._moments.preprocess()
            print('Preprocessing events...')
            self._events.preprocess()
            self._initSegments()
            self.__preprocess_flag = True
        else:
            pass


    @property
    def transition_graph(self,):
        if '_trans_graph' not in self.__dict__.keys():
            mergeSegmentGraphsForGame(game_segments)
        return(self._trans_graph)


class GameMoments(GameSubpartFull):


    _SUB_TYPE_NAME = 'moments'


    def __init__(self, game_info, movements_info, debug_mode=False):
        self._initGameAttributes(game_info)
        self._data = movements_info
        self._debug_mode = debug_mode
        self.__preprocess_flag = False


    def preprocess(self, ):
        if not self.__preprocess_flag:
            self._createMoments()
            self._data = None
            self._ppMoments()
            self.__preprocess_flag = True
        else:
            pass


    def _createMoments(self,):
        mpp = momentsHelper.MomentsPreprocess(self,
                                              debug_mode = self._debug_mode)
        cols = mpp.meta.columns; cols = cols.insert(0, 'Index')
        self.moments = [Moment(mom, met) for (mom, met) in \
                        zip(list(mpp.moments.values()),
                            [{k : v for (k,v) in zip(cols, record)} \
                             for record in mpp.meta.to_records()])]
        self._count = len(self.moments)


    def _ppMoments(self,):
        for m in self.moments:
            m.preprocess()


class GameEvents(GameSubpartFull):

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
                        

    def __init__(self, game_info, pbp_info):
        self._initGameAttributes(game_info)
        self.pbp = eventsHelper.preprocessPbp(pbp_info)
        self.__preprocess_flag = False
        

    def ix(self, i):
        return(GameSubpartBasic.__getitem__(self, i,
                                            item_key = '_events'))
   

    def preprocess(self,):
        if not self.__preprocess_flag:
            self._determinePbpNames()
            self._createEventsIndi()
            self._determinePeriods()
            self._playersOnCourt()
            self._createEventsGroups()
            for e in self.events:
                e.preprocess()
            self.__preprocess_flag = True
            
        else:
            pass


    def _determinePbpNames(self,):
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


    def _determinePeriods(self,):
        periods = sorted(list(set([ev['PERIOD'] for ev in self._events])))
        self.periods = periods


    def _playersOnCourt(self,):
        eventsHelper.playersForEventsGame(self)


    def _createEventsIndi(self,):
        
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


    def _createEventsGroups(self,):

        self._events2event_list  = \
                      eventsHelper.splitEventsBySubsQuarters(self._events)
        self.events = [Events([self.ix(i) for i in el], j) \
                       for j,el in enumerate(self._events2event_list)]
                

    @property
    def ball_transitions(self,):
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
        self.__preprocess_flag = False


    def preprocess(self,):
        if not self.__preprocess_flag:
            if self._moment:
                self._moment.preprocess()
            if self._events:
                self._events.preprocess()
            self.__preprocess_flag = True


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
    def _player_ids(self,):
        p = self.players['home'].copy()
        p.extend(self.players['away'])
        p = sorted(p)
        return(p)


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


    @property
    def ball_transitions(self,):
        if '_ball_transitions' not in self.__dict__.keys():
            segmentsHelper.matchEventsMomentsTransitions(self,
                                                         BallTransition)
        return(self._ball_transitions)


    @property
    def events_ball_transitions(self,):
        if "_ebt" not in self.__dict__.keys():
            if self.eventsId != None:
                cols = list(self._events.ball_transitions.columns)
                cols.insert(0, 'ind')
                self._ebt = [EventBallTransition({k : v \
                                                  for (k,v) in zip(cols, trans)}) \
                            for trans in self._events.ball_transitions.itertuples()]
                self._ebt = [e for e in self._ebt if e['TransitionType'] not in \
                             ['MadeShot', 'MissShot',
                              'Turnover', 'Rebound',
                              'Steal', 'Inbounds'] \
                             and e['ToPlayer'] != e['FromPlayer']]
                for i, et in enumerate(self._ebt):
                    et['ind'] = i
            else:
                self._ebt = []
        return(self._ebt)


    @property
    def moment_ball_transitions(self,):
        if "_mbt" not in self.__dict__.keys():
            if self.momentId != None:
                cols = list(self._moment.ball_transitions.columns)
                cols.insert(0, 'ind')
                self._mbt = [MomentBallTransition({k : v \
                                                   for (k,v) in zip(cols, trans)}) \
                            for trans in self._moment.ball_transitions.itertuples()]
            else:
                self._mbt = []
        return(self._mbt)


    @property
    def ball_trans_graph(self,):
        if '_trans_graph' not in self.__dict__.keys():
            nodes = self._player_ids.copy()
            nodes.extend(['FAIL', 'SUCCESS', 'TURNOVER',
                          'STEAL', 'INBOUNDS',
                          'REBOUND', 'OFFREBOUND', 'DEFREBOUND'])
            self._trans_graph = {'Edges' : segmentsHelper.\
                                 transitions2graph(self.ball_transitions),
                                 'Nodes' : nodes}
        return(self._trans_graph)
    


class Moment(GameSubpartBasic):
    # All functionality that has been constructed for analyzing
    # the moment data (distances, plots, etc) goes in this class

    def __init__(self, moment, meta):
        self._data = moment
        self._meta = meta
        self._count = self._data.shape[0]
        self.__preprocess_flag = False


    def preprocess(self, ):
        if not self.__preprocess_flag:
            self.__preprocess_flag = True
        else:
            pass


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
    def players(self, ):
        return({'home' : list(self._meta['HomePlayers'].copy()),
                'away' : list(self._meta['AwayPlayers'].copy())})

    @property
    def _player_ids(self,):
        p = self._meta['PlayerIds'].copy()
        p.remove(-1)
        return(p)


    @property
    def events(self,):
        return(self._meta['EventIds'])


    @property
    def ball_transitions(self,):
        if '_transitions' not in self.__dict__.keys():
            self._transitions = momentsCalculations.\
                                determineBallTransitions(self._data,
                                                         self._player_ids.copy(),
                                                         self.period,
                                                         self.ball_posessions)
        return(self._transitions)
                                                                

    @property
    def ball_posessions(self,):
        if '_ball_poss' not in self.__dict__.keys():
            self._ball_poss = momentsCalculations.\
                              determineBallPosessions(self._data,
                                                      self._player_ids.copy())
        return(self._ball_poss)


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

        self.events = events
        self._ind = ind
        self._count = len(events)
        self.__preprocess_flag = False


    def __getitem__(self, i):
        return(GameSubpartBasic.__getitem__(self, i))


    def __str__(self,):
        return(str(self.events))


    def _determineEventsType(self,):
        if self.events[0]['Event'] in ['SUB_IN', 'SUB_OUT']:
            self._event_type = 'SUB'
        elif self.events[0]['Event'] == 'TIMEOUT' \
             and len(self.events) == 1:
            self._event_type = 'TIMEOUT'
        else:
            self._event_type = 'REGULAR_PLAY'       


    def preprocess(self,):
        if not self.__preprocess_flag:
            self._determineEventsType()
            self.__preprocess_flag = True
        else:
            pass
    

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
        return(self[0]['PlayersOnCourt'].copy())


    @property
    def _player_ids(self,):
        p = self.players['home'].copy()
        p.extend(self.players['away'])
        p = sorted(p)
        return(p)


    @property
    def ind(self,):
        return(self._ind)


    @property
    def event_type(self,):
        return(self._event_type)


    @property
    def ball_transitions(self,):
        if '_transitions' not in self.__dict__.keys():
            if self.event_type == 'SUB':
                self._transitions = eventsHelper.\
                                    EMPTY_TRANSITIONS_PLACEHOLDER
            else:
                ef = eventsHelper.TransitionsFinder(self.events,
                                                    self.null_event)
                ef.getTransitions()
                if len(ef.event_dict) == 1:
                    self._transitions = ef.event_dict[0]['TransitionsData']
                elif len(ef.event_dict) == 0:
                    self._transitions = eventsHelper.\
                                        EMPTY_TRANSITIONS_PLACEHOLDER
        return(self._transitions)



