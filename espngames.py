
import retrieveEspnNbaData


'''
nba_root    = "http://scores.espn.go.com/nba/scoreboard?date=" + date
nba_pbp_all = "http://scores.espn.go.com/nba/playbyplay?gameId=" + gameID + "&period=0"
nba_box     = "http://scores.espn.go.com/nba/boxscore?gameId=" + gameID
ncaa_root   = "http://scores.espn.go.com/ncb/scoreboard?date=" + date
'''
'''Links and paths'''
nba_ext         = "http://scores.espn.go.com/nba/recap?gameId="
nba_box         = "http://scores.espn.go.com/nba/boxscore?gameId="
nba_pbp         = "http://scores.espn.go.com/nba/playbyplay?gameId="
nba_shots       = "http://sports.espn.go.com/nba/gamepackage/data/shot?gameId="


MASTER_DATA_LIST = ['recap',
                    'play_by_play',
                    'player_stats', 'game_stats',
                    'shots',
                    'season',
                    'date']

class NBAGame():


    def __init__(self, game_id,
                 season = '', date = '',
                 verbose=False):
        """
        :type game_id: str
        :param game_id: ESPN game id for game in question

        :type verbose: bool
        :param verbose: indicates whether information regarding processes
        are printed to output
        """

        self.game_type = 'NBA'
        if season:
            self.season = season
        if date:
            self.date = date
        self.game_id = game_id
        self.verbose = verbose


    def initFromEspn(self):
        """

        """
        self.retrieveRecapFromUrl()
        self.retrievePBPFromUrl()
        self.retrieveBoxScoreFromUrl()
        self.retrieveShotsFromUrl()


    def checkDbForGame(self, db_conn):
        """
        Checks to see game has been initialized in the DB.
        """
        pass


    def retrieveGameData(self):
        """
        Wrapper for running modules to retreive data specifified
        by self.game_id
        """
##        self.retrieveRecap()
        self.retrievePBP()
        self.retrieveBoxScore()
        self.retrieveShots()


    def retrieveRecap(self):
        """
        Retrieves "recap" data for game.  Checks if game info is in
        DB.  If yes, get from there.  Else, go to ESPN and pull data
        from there.

        Todo:  add functionality to pull data from DB
        """
        self.retrieveRecapFromUrl()


    def retrieveRecapFromUrl(self):
        """
        Retreive recap / summary data for game from ESPN URL.
        """
        
        try:
            url = nba_ext + str(self.game_id)
            if self.verbose: print(url)
            ext = retrieveEspnNbaData.dataFromUrl(url,
                                                  'ext',
                                                  self.game_id)
        except ValueError:
            # need some stuff to spit out error info...
            print('Failed to retreive recap for game ' +\
                  str(self.game_id))
            ext = dict()
        self.recap = ext
    

    def retrievePBP(self):
        """
        Retrieves "play-by-play" data for game.  Checks if game info is in
        DB.  If yes, get from there.  Else, go to ESPN and pull data
        from there.

        Todo:  add functionality to pull data from DB
        """
        self.retrievePBPFromUrl()


    def retrievePBPFromUrl(self):
        """
        Retrieve play-by-play data for game from ESPN URL.
        """
        
        try:
            url = nba_pbp + str(self.game_id) + "&period=0"
            if self.verbose: print(url)
            pbp = retrieveEspnNbaData.dataFromUrl(url,
                                                  'pbp',
                                                  self.game_id)
        except ValueError:
            # need some stuff to spit out error info...
            print('Failed to retreive play-by-play for game ' + str(gameid))
            pbp = dict()
        self.play_by_play = pbp
    

    def retrieveBoxScore(self):
        """
        Retrieves "box score" data for game.  Checks if game info is in
        DB.  If yes, get from there.  Else, go to ESPN and pull data
        from there.

        Todo:  add functionality to pull data from DB
        """
        self.retrieveBoxScoreFromUrl()


    def retrieveBoxScoreFromUrl(self):
        """
        Retrieve box score information for game from ESPN URL.
        """
        
        try:
            url = nba_box + str(self.game_id)
            if self.verbose: print(url)
            box = retrieveEspnNbaData.dataFromUrl(url,
                                                  'box',
                                                  self.game_id)
            if box:
                self.player_stats = box['player_info']
                self.game_stats = box['game_info']
            else:
                self.player_stats = {}
                self.game_stats = {}
        except ValueError:
            # need some stuff to spit out error info...
            print('Failed to retreive box score for game ' + str(gameid))
            box = dict()


    def retrieveShots(self):
        """
        Retrieves "shots" data for game.  Checks if game info is in
        DB.  If yes, get from there.  Else, go to ESPN and pull data
        from there.

        Todo:  add functionality to pull data from DB
        """
        self.retrieveShotsFromUrl()
    

    def retrieveShotsFromUrl(self):
        """
        Retrieve shot information for game from ESPN URL.
        """
        try:
            url = nba_shots + str(self.game_id)
            if self.verbose: print(url)
            shots = retrieveEspnNbaData.dataFromUrl(url,
                                                    'shots',
                                                    self.game_id)
        except ValueError:
            # need some stuff to spit out error info...
            print('Failed to retreive shot locations for game ' + str(gameid))
            shots = list()
        self.shots = shots


    def dataToDict(self, which_data=MASTER_DATA_LIST):
        """
        Places information specified by which_data about the game
        into a single dictionary object. "game_id" is always added
        to the dictionary.
        """
        data_dict = {}
        data_dict["game_id"] = self.game_id
        for data_label in which_data:
            if hasattr(self, data_label):
                data_dict[data_label] = getattr(self, data_label)
            else:
                print("%s is not an attribute of game %s" % \
                      (data_label, self.game_id))
        return data_dict
    


if __name__=='__main__':
    gameIds = ['400579038', '400579039', '400579040',
               '400579044', '400579041', '400579042',
               '400579043', '400579045', '400579046',
               '400579047', '400579048', '400579049']
    games = []
    for gameId in gameIds[:3]:
        print("Retrieving data for game id %s" % gameId)
        game = NBAGame(gameId)
        game.retrieveGameData()
        games.append(game)
        print(game.game_stats['stats'])
        data_dict = game.dataToDict()
        print(data_dict['game_stats']['stats'])
        print("Finished retrieving data for game.")
    print "Process complete."

