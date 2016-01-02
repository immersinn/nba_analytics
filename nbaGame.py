
##import gameHelper
import momentsHelper
import eventsHelper
import segmentsHelper


class NBAGameBasic:


    def __init__(self, teams,
                 player_ids, player_names, pid_name_lookup,
                 **kargs):
        self.set_attrs(teams,
                       player_ids, player_names, pid_name_lookup,
                       **kargs)


    def set_attrs(self, teams,
                  player_ids, player_names, pid_name_lookup,
                  **kargs):
        self.teams = teams
        self.pids = player_ids
        self.pnames = player_names
        self.pid_name_lookup = pid_name_lookup


    def game_info_dict(self,):



class NBAGameAnalysis(NBAGameBasic):


    def __init__(self, teams,
                 player_ids, player_names, pid_name_lookup,
                 moments_raw, pbp_raw,
                 **kargs):
        self.set_attrs(teams,
                       player_ids, player_names, pid_name_lookup,
                       moments_raw, pbp_raw,
                       **kargs)

    def set_attrs(self, teams,
                  player_ids, player_names, pid_name_lookup,
                  moments_raw, pbp_raw,
                  **kargs):
        NBAGameBasics.set_attrs(teams,
                                player_ids, player_names, pid_name_lookup,
                                **kargs)
        self.moments_data = moments_raw
        self.events_data = pbp_raw


    def init_data(self,):
        self.init_moment_class()
        self.init_events_class()
        self.init_segments_class()


    def init_moment_class(self):
        self.moments = GameMoments(self.game_info_dict(),
                                   self.player_info_dict(),
                                   self.moments_raw))


    def init_event_class(self):
        self.events = GameEvents(self.game_info,
                                 self.player_info,
                                 self.pbp_raw))


    def init_segment_class(self):
        self.segments = GameSegments(self.game_info_dict(),
                                     self.player_info_dict(),
                                     self))


    def extractTransitionGraph(self,):
        self.init_segment_class()
        self.segments.preprocess()
        self.transition_graph = self.segments.extractTransitionGraph()
        

class GameSegmentsBasic:


    def __init__(self, **kargs):
        self.set_attrs(kargs)


    def set_attrs(self, game_info, player_info):
        self.set_game_info(game_info)
        self.set_player_info(player_info)


class GameSegments(GameSegmentsBasic):


    def __init__(self, game_info, player_info, **kargs):
        self.set_attrs(game_info, player_info)
        if 'game' in kargs.keys():
            self.init_moments_events(game)
        elif 'moments' in kargs.keys() and 'events' in kargs.keys():
            self.moments = moments
            self.events = events
        else:
            raise AttributeError
        self.__preprocess_flag = False


    def init_moments_events(self, Game):
        self.moments = GameMoments(Game)
        self.events = GameEvents(Game)


    def preprocess(self,):
        if not self.__preprocess_flag:
            self.graph_moments.preprocess()
            self.graph_events.preprocess()
            self.createSegments()
            # Other stuff...
            self.__preprocess_flag = True
        else:
            pass


    def align_moments_events(self,):
        self.ms_matches = segmentsHelper.matchEventsMoments(self.events,
                                                            self.moments)


    def createSegments(self,):
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
        self.game_segments.append(new)


    def extractTransitionGraph(self,):
        self.preprocess()


class GameEvents:
    # Individual events should be accessible by an index
    # i.e., events[k] should return the k-th event in events

    def preproces(self,):
        # Do necessary transformation on raw semi-structured pbp
        # as necessary
        pass


    def createEvents(self,):
        # create a list of Event instances;
        # splits performed on substitutions and
        # quarters
        pass


    def players_on_court(self,):
        # attempt to determine which players on on
        # the court at a given time
        pass


class GameMoments:
    # Individual moments should be accessible by an index

    pass



class Segment(object):

    def __init__(events_id, events,
                 moment_id, moment):
        self.eid = events_id
        self.events = events
        self.mid = moment_id
        self.moment = moment


    def preprocess(self,):
        pass


class Moment(object):

    pass


class Events(object):

    pass





        
        
