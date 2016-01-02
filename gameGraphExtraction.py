
from nba_analytics import momentsHelper
from nba_analytics import eventsHelper
from nba_analytics import segmentsHelper



class ExtractGameGraph:


    def __init__(self, game_pbp_raw, game_moments_raw, game_meta):
        """
        self.name2id =
        self.pbp_names =
        self.pbp2id =
        self.team_names =
        Other??
        """
        pass


    def runPipeline(self,):

        self.prepareData()
        self.createSegments()
        self.extractBallTransitions()
        return(self.getTeamTransitions)


    def prepareData(self,):
        self.prepMoments
        self.prepEvents


    def prepMoments(self,):
        self.moments = momentsHelper.preprocessSegments(self.game_moments_raw)


    def prepEvents(self,):
        """
        i)    convert to a data frame
        ii)   add index
        iii)  add game clock
        iv)   use the parser (?)
        iv)   split by substitutions and quarters (?)
        """
        pbp = eventsHelper.preprocessPbp(self.game_pbp_raw)
        self.esf = eventsHelper.EventsFinder(pbp,
                                          self.pbp_names,
                                          self.team_names,
                                          self.pbp2id)
        self.esf.getEvents()
        self.events = self.esf.event_dict
        

    def createSegments(self,):
        """
        i)    align moments and events
        ii)   merge moments and events (see pbpPipeline)
        iii)  initialize a Segment object from the (moment, event, meta) tuple
        iv)   assign to self.segments
        """
        self.segments = [Segment(s) for s in \
                         segmentsHelper.mergeEventsMoments(\
                             self.events, self.moments)]


    def extractBallTransitions(self,):
        self.ball_transitions = []
        # Should the transitions already be extracted?
        for segment in self.segments:
            self.ball_transitions.extend(segment.extractTransitions())


    def getTeamBallTransitions(self,):
        team_edge_lists = []
        edge_list = [bt.toDict() for bt in self.ball_transitions]
        for t in self.teams:
            team_edge_lists.append({'Team' : t,
                                    'Transitions' : [btd for btd in edge_list \
                                                     if btd['team']==t]})
        return(team_edge_lists)


class Segment:

    def __init__(self, segment):
        """
        segment {'moment' : moment_data,
                 'events' : pbp_data,
                 'SegmentInfo' : {},
                 'PlayerInfo' : {}
                 }
        """
        pass


    def extractTransitions(self,):
        """
        i)    parse and process the pbp data (where are transitions stuff)
        ii)   process the moments data (posession gaps stuff)
        iii)  match pbp events to posession gaps
        iv)   build complete list of all transition types

        See ipython notebook, "Match Ball Transitions to Posession Gaps"
        this will be in 'segmentsHelper'
        """
        pass
    

class BallTransition(object):

    def __init__(self,):
        pass


    def toDict(self,):
        """
        Returns all info related to the bt as a dictionary.
        Attributes:
            srcId : player id OR sink name
            srcName : player name OR sink name
            dstId : player id OR sink name
            dstName : player name OR sink name
            team : name of team associated with transition
            gameclock : gameclock at time of event
            ttypeId : transition type id from PBP OR pass
            ttypeName : transition type description from pbp OR pass

        """
        d = {}
        return(d)

    
