
import re
import pandas

"""
Format of a description entry:
    * MISS (optional)
    * Player.ShorthandName (all one 'word', no spaces)
    * If shot, shot description
    * If turnover, turnover description
    * REBOUND / S.FOUL / FOUL / STEAL / BLOCK
    * If made shot, (XX PTS)
    * Player, team stats regarding event that just transpired

"""



##def getEventPlayer(event_description,
##                   player_names=[],
##                   team_names=[],
##                   remove_bracket = False):
##    
##    s = detEventState(event_description)
##    if s and player_names:
##        if remove_bracket:
##            ed = re.split('\(', event_description)[0]
##        else:
##            ed = event_description
##        p = detPlayer(ed, player_names, team_names)
##    else:
##        p = ['']
##        
##    return(s, p)
##
##
##def detPlayer(event_description, 
##              player_names, team_names,
##              ordered=False):
##    if ordered:
##        pass
##    else:
##        teams   = [t for t in team_names \
##                   if re.search(t, event_description)]
##        players = [p for p in player_names \
##                   if re.search(p, event_description)]
##        players.extend(teams)
##    return(players)
##
##
##def getPlayer(e, p):
##    print('broken call to get player func')

    

def detEventType(event_line):
    """
    event message types and select action types:

    1 --> shot made
    2 --> shot missed
    3 --> free throw make and miss
    4 --> rebound
    5 --> turnover
        1 --> bad pass + steal
        2 --> lost ball + steal
        3 -->
        4 --> traveling
        5 --> foul turnover
        11 --> shot clock
    6 --> (offensive, shooting, etc) foul
    7 --> Violation
        2 --> Defensive Goaltending
        5 --> Kicked Ball
    8 --> sub
    9 --> Full timeout
    10 --> jump ball
    11 --> ???
    12 --> quarter start
    13 --> quarter end / game end
    """
    
    if event_line.EVENTMSGTYPE == 1:
        state = 'MadeShot'
    elif event_line.EVENTMSGTYPE == 2:
        state = 'MissShot'
    elif event_line.EVENTMSGTYPE == 3:
        state = 'FreeThrow'
    elif event_line.EVENTMSGTYPE == 4:
        state = 'Rebound'
    elif event_line.EVENTMSGTYPE == 5:
        state = 'Turnover'
    elif event_line.EVENTMSGTYPE == 6:
        state = 'Foul'
    elif event_line.EVENTMSGTYPE == 7:
        state = 'Violation'
    elif event_line.EVENTMSGTYPE == 8:
        state = 'Sub'
    elif event_line.EVENTMSGTYPE == 9:
        state = 'Timeout'
    elif event_line.EVENTMSGTYPE == 10:
        state = 'JumpBall'
    elif event_line.EVENTMSGTYPE == 11:
        state = 'UKWN'
    elif event_line.EVENTMSGTYPE == 12:
        state = 'QuarterStart'
    elif event_line.EVENTMSGTYPE == 13:
        state = 'QuarterEnd'
    else:
        state = event_line.EVENTMSGTYPE
    return(state)

       


####################

class EventsFinder:
    
    def __init__(self, play_by_play, 
                 player_names, team_names,
                 name_pid_lookup):
        self.pbp = play_by_play
        self.pnames = player_names
        self.tnames = team_names
        self.plookup = name_pid_lookup
        self.indx = 0
        self.max_indx = self.pbp.shape[0]
        self.event_dict = {}
        self.event_count = 0
        self.current = []
        
    
    def getEvents(self,):
        while self.indx < self.max_indx:
            ne = SinglePosChangeFinder(self.pbp,
                                       self.pnames,
                                       self.tnames,
                                       self.plookup,
                                       self.max_indx,
                                       self.indx)
            ne.getPosChange()
            self.current.extend(ne.transitions)
            self.indx = ne.indx + 1
            if ne.state == 'EOL':
                if self.current:
                    new = {}
                    new['Quarter'] = self.current[0]['quarter']
                    new['StartTime'] = self.current[0]['gc']
                    new['EndTime'] = self.current[-1]['gc']
                    new['EventsData'] = self.current
                    self.event_dict[self.event_count] = new
                    self.event_count += 1
                    self.current = []


####################


MAIN_EVENTS = ['MissShot',
               'MadeShot',
               'Turnover']
STOP_EVENTS = ['QuarterEnd',
               'Sub']


class SinglePosChangeFinder:
    
    def __init__(self, 
                 play_by_play, 
                 player_names, teams,
                 name_pid_lookup,
                 max_indx, start_indx=0):
        self.pbp = play_by_play
        self.pnames = player_names
        self.tnames = teams
        self.plookup = name_pid_lookup
        self.pind = play_by_play.index
        self.indx = start_indx
        self.max_indx = max_indx
        self.transitions = []
        self.initState()
        
        
    def getPosChange(self,):
        self.initState()
        self.evalState()
        
    
    def initState(self):
        self.state = ''
        self.indx -= 1
        #while not self.state and self.indx < self.max_indx - 1:
        while not self.state:
            self.indx += 1
            self.determineState()
            

    def determineState(self,):
        
        # Initilize event info
        self.setCurrEvent()
        
        event_msg_state = detEventType(self.current)
        
        if event_msg_state in MAIN_EVENTS:
        
            self.updateEventInfo()
            if self.event_info['home_e'] in MAIN_EVENTS and \
               self.event_info['away_e'] in MAIN_EVENTS:
                self.state = 'UKWN'
                self.event_info['Team'] = u''
            elif self.event_info['home_e'] in MAIN_EVENTS:
                self.state = self.event_info['home_e']
                self.event_info['Team'] = 'home'
            elif self.event_info['away_e'] in MAIN_EVENTS:
                self.state = self.event_info['away_e']
                self.event_info['Team'] = 'away'
                
        elif event_msg_state in STOP_EVENTS:
            self.state = 'EOL'
            
##    
##    def evalState(self):
##        if self.state == 'MadeShot':
##            self.evalMadeShot()
##        elif self.state == 'MissShot':
##            self.evalMissShot()
##        elif self.state == 'Turnover':
##            self.evalTurnover()
##        elif self.state =='EOL':
##            pass
##
##            
##    def getEvent(self, index=-1):
##        if index < 0:
##            index = self.indx
##        return(self.pbp.ix[self.pind[index]])
##    
##    
##    def setCurrEvent(self, index=-1, event=''):
##        if event:
##            self.current = event
##        else:
##            self.current = self.getEvent(index=index)
##            
##    
##    def getDescrip(self, hORa=''):
##        if hORa == '':
##            hORa = self.getTeam()
##        if hORa == 'home':
##            d = self.current.HOMEDESCRIPTION
##        elif hORa == 'away':
##            d = self.current.VISITORDESCRIPTION
##        elif hORa == 'neutral':
##            d = self.current.NEUTRALDESCRIPTION
##        else:
##            d = None
##        if not d:
##            d = u''
##        return(d)
##        
##        
    def getTeam(self):
        if 'Team' in self.event_info:
            return(self.event_info['Team'])
        else:
            return('')
        
        
    def getRevTeam(self):
        if 'Team' in self.event_info:
            if self.event_info['Team'] == 'home':
                return('away')
            elif self.event_info['Team'] == 'away':
                return('home')
            else:
                return(u'')
        else:
            return(u'')
##        
##        
##    def getPlayer(self, pname='', hORa=''):
##        if not pname:
##            if hORa == '':
##                hORa = self.getTeam()
##            if hORa == 'home':
##                p = self.event_info['home_p']
##            elif hORa == 'away':
##                p = self.event_info['away_p']
##            else:
##                p = u''
##        else:
##            p = pname
##            
##        if type(p) == list:
##            p = p[0]
##            
##        try:
##            pid = self.plookup[p]
##        except KeyError:
##            pid = p
##            
##        return(pid)
##    
##    
##    def getGameClock(self,):
##        return(self.current['GAMECLOCK'])
####        return(self.event_info['game_clock'])
####
####
##    def getQuarter(self,):
##        return(self.current['PERIOD'])
####        return(self.event_info['quarter'])
            
            
##    def updateEventInfo(self,
##                        remove_bracket = True):
##        """
##        Examines text from play_by_play for home, away, neutral
##        (HOMEDESCRIPTION, VISITORDESCRIPTION, NEUTRALDESCRIPTION, resp.)
##        """
##        hs, hp = getEventPlayer(self.getDescrip('home'), 
##                                player_names = self.pnames,
##                                team_names = self.tnames,
##                                remove_bracket = remove_bracket)
##        vs, vp = getEventPlayer(self.getDescrip('away'), 
##                                player_names = self.pnames,
##                                team_names = self.tnames,
##                                remove_bracket = remove_bracket)
##        ns, _ = getEventPlayer(self.getDescrip('neutral'))
##        gc    = time2Gc(self.current.PCTIMESTRING)
##        qr    = int(self.current.PERIOD)
##        
##        self.event_info = {'home_e' : hs, 'away_e' : vs, 'neutral_e': ns,
##                           'home_p' : hp, 'away_p' : vp,
##                           'quarter' : qr, 'game_clock' : gc}
##        self.determineTeam()
        
    
##    def determineTeam(self):
##        if self.event_info['home_e'] and self.event_info['away_e']:
##            team = 'both'
##        elif self.event_info['home_e']:
##            team = 'home'
##        elif self.event_info['away_e']:
##            team = 'away'
##        elif self.event_info['neutral_e']:
##            team = 'neutral'
##        else:
##            team = u''
##        self.event_info['Team'] = team
    
    
##    def evalMadeShot(self):
##        # Check for shooting foul on def team's pbp
##        # How does this change if a off foul committed?
##        
##        self.evalAssist()
##        
##        self.fr_player = self.getPlayer()
##        self.transitions.append({'to' : 'SUCCESS',
##                                 'from' : self.fr_player,
##                                 'ttype' : 'MadeShot',
##                                 'quarter' : self.getQuarter(),
##                                 'gc' : self.getGameClock()})
##        
##        self.evalShootFoul()
##        if self.state == 'Foul':
##            self.evalFoulShots()
##            if self.state == 'MissedFoul':
##                self.evalRebound()
##                if self.state == 'Transition':
##                    self.updateTransition()
##                else:
##                    # Error
##                    pass
##            elif self.state == 'MadeFoul':
##                self.addInboundsTransition()
##            elif self.state == 'BREAK':
##                self.b()
##        else:
##            self.addInboundsTransition()
            
            
##    def evalMissShot(self):
##        
##        self.evalAssist()
##        
##        self.fr_player = self.getPlayer()
##        self.transitions.append({'to' : 'FAIL',
##                                 'from' : self.fr_player,
##                                 'ttype' : 'MissShot',
##                                 'quarter' : self.getQuarter(),
##                                 'gc' : self.getGameClock()})
##        
##        self.evalShootFoul()
##        if self.state == 'Foul':
##            self.evalFoulShots()
##            if self.state == 'MissedFoul':
##                self.evalRebound()
##                if self.state == 'Transition':
##                    self.updateTransition()
##                else:
##                    # Error
##                    pass
##            elif self.state == 'MadeFoul':
##                self.addInboundsTransition()
##            elif self.state == 'BREAK':
##                self.b()
##        else:
##            self.evalRebound()
##            if self.state == 'Transition':
##                self.updateTransition()
##            else:
##                # Error
##                pass
            
            
##    def evalAssist(self,):
##        # Accesses and assigns players in a different manner than everything
##        # else in this class.  Need to make consistant across all
##        descrip = self.getDescrip()
##        if re.search(r'AST|Ast', descrip):
##            descrip = [w.strip('(').strip(')') for w in descrip.split()]
##            self.transitions.append({'to' : self.getPlayer(pname=descrip[0]),
##                                     'from' : self.getPlayer(pname=descrip[-3]),
##                                     'ttype' : 'Pass',
##                                     'tsubtype' : 'Assist',
##                                     'quarter' : self.getQuarter(),
##                                     'gc' : self.getGameClock()})
            
            
##    def evalTurnover(self,):
##        
##        self.fr_player = self.getPlayer()
##        self.transitions.append({'to' : 'TURNOVER',
##                                 'from' : self.fr_player,
##                                 'ttype' : 'Turnover',
##                                 'quarter' : self.getQuarter(),
##                                 'gc' : self.getGameClock()})
##        descrip = self.getDescrip(self.getRevTeam())
##        if re.search(r'STEAL|Steal', descrip):
##            self.to_player = self.getPlayer(hORa=self.getRevTeam())
##            self.transitions.append({'to' : self.to_player,
##                                     'from' : 'TURNOVER',
##                                     'ttype' : 'Steal',
##                                     'quarter' : self.getQuarter(),
##                                     'gc' : self.getGameClock()})
##            self.trans_type = self.state + ' Steal'
##            self.updateTransition()
##        else:
##            self.addInboundsTransition()
            
            
            
##    def evalShootFoul(self):
##        # Looks if shooting foul occuring during shot
##        self.setCurrEvent(self.indx + 1)
##        descrip = self.getDescrip(self.getRevTeam())
##        pat = re.compile(r'S.FOUL|S.Foul')
##        if re.search(pat, descrip):
##            self.indx += 1
##            self.state = 'Foul'
            
    
##    def evalFoulShots(self):
##        # Parses through foul shots and determines if
##        # last one was made or missed
##        self.setCurrEvent(self.indx + 1)
##        descrip = self.getDescrip(self.getTeam())
##        if re.search(r'Free Throw [1-3] of [1-3]', descrip):
##            if re.search(r'MISS', descrip):
##                self.state = 'MissedFoul'
##            else:
##                self.state = 'MadeFoul'
##            self.indx += 1
##            self.evalFoulShots()
##        elif re.search(r'SUB', descrip):
##            self.indx = len(self.pbp) + 1
##            self.state = 'EOL'
##        else:
##            # Roll back event to last Foul state
##            self.setCurrEvent()
            
            
##    def evalRebound(self):
##        self.setCurrEvent(self.indx + 1)
##        pat = re.compile(r'REBOUND|Rebound')
##        for t in ['home', 'away']:
##            descrip = self.getDescrip(t)
##            if re.search(pat, descrip):
##                self.to_player = self.getPlayer(pname=detPlayer(descrip,
##                                                                self.pnames,
##                                                                self.tnames)[0])
##                self.trans_type = self.state + ' Rebound'
##                self.state = 'Transition'
##                self.indx += 1
##                break
            
            
##    def updateTransition(self,):
##        
##        overall = {'from' : self.fr_player,
##                   'to' : self.to_player,
##                   'ttype' : self.trans_type,
##                   'quarter' : self.getQuarter(),
##                   'gc' : self.getGameClock()}
##        self.transitions.append(overall)
##        
##        if re.search('Rebound', self.trans_type):
##            self.transitions.append({'from' : 'REBOUND',
##                                     'to' : self.to_player,
##                                     'ttype' : 'Rebound',
##                                     'quarter' : self.getQuarter(),
##                                     'gc' : self.getGameClock()})
##            
##            
##    def addInboundsTransition(self,):
##
##        if self.state == 'MadeShot':
##            self.transitions.append({'from' : self.fr_player,
##                                     'to' : 'TBD',
##                                     'ttype' : 'MadeShot Inbounds',
##                                     'quarter' : self.getQuarter(),
##                                     'gc' : self.getGameClock()})
##            
##        self.transitions.append({'from' : 'INBOUNDS',
##                                 'to' : 'TBD',
##                                 'ttype' : 'Inbounds',
##                                 'quarter' : self.getQuarter(),
##                                 'gc' : self.getGameClock()})
        
