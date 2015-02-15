"""
This file grabs complete play-by-play pages and box score pages for games
specified; run from terminal with:

python getESPNPagesNBA.py date|gameidfile|gameid [outputname]

where the first arg can be: a date with the form YYYYMMDD, a file containing
a list of ESPN game ids, or a single ESPN game id; the second, optional arg
is the root name of the output pickle files, one for the play-by-play raw
pages, and the other for the box score raw pages; data format is dictionaries
with the ESPN game ids as keys and the raw pages as values; if a date is used
as input, the program attempts to locate that page, and extracts the
ESPN game ids from the scores summary page for that date;
"""

import sys

import retrieveEspnNbaData


'''
nba_root    = "http://scores.espn.go.com/nba/scoreboard?date=" + date
nba_pbp_all = "http://scores.espn.go.com/nba/playbyplay?gameId=" + gameID + "&period=0"
nba_box     = "http://scores.espn.go.com/nba/boxscore?gameId=" + gameID
ncaa_root   = "http://scores.espn.go.com/ncb/scoreboard?date=" + date
'''
'''Links and paths'''
nba_root        = "http://scores.espn.go.com/nba/scoreboard?date="
nba_ext         = "http://scores.espn.go.com/nba/recap?gameId="
nba_box         = "http://scores.espn.go.com/nba/boxscore?gameId="
nba_pbp         = "http://scores.espn.go.com/nba/playbyplay?gameId="
nba_shots       = "http://sports.espn.go.com/nba/gamepackage/data/shot?gameId="

ncaa_root       = "http://scores.espn.go.com/ncb/scoreboard?date="

default_path    = "/Users/sinn/NBA-Data-Stuff/DataFiles"

root_dict       = {'NBA':nba_root,
                   'NCAM':ncaa_root,
                   }
null_value      = '&nbsp;'
space_holder = u'\xc2\xa0'                  # curiousior and curiousior (sp?)
max_args        = 2


class NBAGame():


    def __init__(self, gameId, verbose=False):
        self.gameId = gameId
        self.verbose = verbose


    def retrieveGameData(self):
##        self.retrieveRecap()
        self.retrievePBP()
        self.retrieveBoxScore()
        self.retrieveShots()


    def retrieveRecap(self):
        """
        Really this is the recap page, but also grabs some other info like game
        location and time, etc; also story analysis of game;
        """
        
        try:
            url = nba_ext + str(self.gameId)
            if self.verbose: print(url)
            ext = retrieveEspnNbaData.dataFromUrl(url, 'ext')
        except ValueError:
            # need some stuff to spit out error info...
            print('Failed to retreive recap for game ' + str(gameid))
            ext = dict()
        self.recap = ext
    

    def retrievePBP(self):
        """
        Given an ESPN game ID grabs play-by-play page, forms it into a
        structured doc;
        """
        
        try:
            url = nba_pbp + str(self.gameId) + "&period=0"
            if self.verbose: print(url)
            pbp = retrieveEspnNbaData.dataFromUrl(url, 'pbp')
        except ValueError:
            # need some stuff to spit out error info...
            print('Failed to retreive play-by-play for game ' + str(gameid))
            pbp = dict()
        self.play_by_play = pbp
    

    def retrieveBoxScore(self):
        """
        Given an ESPN game ID grabs the box score feed page, turns it into
        a structured doc;
        """
        
        try:
            url = nba_box + str(self.gameId)
            if self.verbose: print(url)
            box = retrieveEspnNbaData.dataFromUrl(url, 'box')
        except ValueError:
            # need some stuff to spit out error info...
            print('Failed to retreive box score for game ' + str(gameid))
            box = dict()
        self.box_score = box
        

    def retrieveShots(self):
        """
        Given an ESPN game ID grabs the shot placement for the game; makes
        structured doc;
        """
        try:
            url = nba_shots + str(self.gameId)
            if self.verbose: print(url)
            shots = retrieveEspnNbaData.dataFromUrl(url, 'shots')
        except ValueError:
            # need some stuff to spit out error info...
            print('Failed to retreive shot locations for game ' + str(gameid))
            shots = list()
        self.shot_locations = shots


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
        print("Finished retrieving data for game.")
    print "Process complete."

