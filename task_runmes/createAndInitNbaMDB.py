#0 Create NBS db in MongoDB
#1 Create game and shots collections in the NBA DB
#2 Grab game ids for the games in the 2008-2009 Season (Full)
#3 Can I add some automated testing in here (e.g. query docs?)
#4 Can I add in a (optional) clean-up step?
####
# Seems to be several missing games.  Should be 1230 Reg Season
# plus 85 playoff games for total of 1315 for this season.  Only
# 1252 at last run.


import sys

sys.path.append('/Users/immersinn/Gits/')

from nba_analytics import espngames
import initGamesFromEspn
from initGamesFromEspn import root_dict
from nba_analytics.dbconns import connectMon



def createAndReturnNbaMdbs():
    gamemdb = connectMon.MongoConn()
    shotmdb = connectMon.MongoConn()
    db_name = 'NBAData'
    game_coll_name = 'Games'
    gamemdb.makeDBConn(db_name)
    gamemdb.makeCollConn(game_coll_name)
    shot_coll_name = 'Shots'
    shotmdb.makeDBConn(db_name)
    shotmdb.makeCollConn(shot_coll_name)
    return {'games':gamemdb,
            'shots':shotmdb}


def main():
    """
    Tuesday, October 28, 2008, and ended on Wednesday, April 15, 2009.
    The 2009 NBA Playoffs started on Saturday, April 18, 2009 and ran
    until Sunday, June 14
    """
    start_date = [2008, 10, 28]
    end_date = [2009, 6, 14]
    dates = initGamesFromEspn.genDateSeq(start_date, end_date)
    root_url = root_dict['NBA']
    dbs = createAndReturnNbaMdbs()
    games = dbs['games']
    shots = dbs['shots']
    for date in dates:
        if int(date) < 20090418:
            season = '20082009Regular'
        else:
            season = '20082009Playoffs'
        game_ids = initGamesFromEspn.retrieveEspnGameIdsForDay(date, root_url)
        tot_ids = len(game_ids)
        print("%s game ids retrieved for %s" % (tot_ids, date))
        for game_id in game_ids:
            print("Game ID: %s" % game_id)
            game = espngames.NBAGame(game_id, season=season)
            game.initFromEspn()
            game_info_dict = game.dataToDict()
            try:
                shot_info_list = game_info_dict.pop('shots')
                shots.MongoInsert(shot_info_list)
            except KeyError:
                print('No shot data for game %s' % game_id)
            games.MongoInsert(game_info_dict)


if __name__=="__main__":
    main()
