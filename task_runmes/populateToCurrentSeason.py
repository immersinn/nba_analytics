

import sys
import pickle
from nba_analytics import espngames
import initGamesFromEspn
from initGamesFromEspn import root_dict
from nba_analytics.dbconns import connectMon


season_info_file = '/home/immersinn/Gits/nba_analytics/task_runmes/NBASeasons.csv'


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


def toDateFormat(sdate):
    """
    Convert data from "YYYYMMDD" string to [YYYY, M, D] list
    """
    assert len(sdate) == 8
    ldate = [int(sdate[:4]), int(sdate[4:6]), int(sdate[6:])]
    return ldate


def main(season_info):

    errs = []
    try:
        for season in season_info:
            s = season['Season']
            start_date = toDateFormat(season['Start'])
            end_date = toDateFormat(season['End'])
            playoff_start = int(season['PlayoffStart'])

            print('Retrieving data for the %s Season' % s)

            dates = initGamesFromEspn.genDateSeq(start_date, end_date)
            root_url = root_dict['NBA']
            dbs = createAndReturnNbaMdbs()
            games = dbs['games']
            shots = dbs['shots']
            for date in dates:
                try:
                    if int(date) < playoff_start:
                        stype = ' '.join([s, 'Regular'])
                    else:
                        stype = ' '.join([s, 'Playoffs'])
                    game_ids = initGamesFromEspn.retrieveEspnGameIdsForDay(date, root_url)
                    tot_ids = len(game_ids)
                    print("%s game ids retrieved for %s" % (tot_ids, date))
                    for game_id in game_ids:
                        try:
                            
                            print("Game ID: %s" % game_id)
                            query = games.query({'game_id' : str(game_id)}, {'game_id' : 1}, verbose=False)
                            if query.count() > 0:
                                print("Game already exists in db; skipping")
                            else:
                                game = espngames.NBAGame(game_id, season=stype)
                                game.initFromEspn()
                                game_info_dict = game.dataToDict()
                                try:
                                    shot_info_list = game_info_dict.pop('shots')
                                    shots.insert(shot_info_list)
                                except KeyError:
                                    print('No shot data for game %s' % game_id)
                                games.insert(game_info_dict)
                        except KeyboardInterrupt:
                            raise KeyboardInterrupt
                        except:
                            print('Error encounterd at document %s' % game_id)
                            new_error = {'game_id' : game_id,
                                         'err_type':sys.exc_info()[0],
                                         'err_msg':sys.exc_info()[1]}
                            errs.append(new_error)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    print('Error encountered at date %s' % date)
                    new_error = {'date' : date,
                                 'err_type':sys.exc_info()[0],
                                 'err_msg':sys.exc_info()[1]}
                    errs.append(new_error)
                        
    finally:
        with open('errorsRetrievingGameData02.pkl', 'w') as f1:
            pickle.dump(errs, f1)


if __name__=="__main__":

    with open(season_info_file, 'r') as f1:
        data = f1.readlines()
        data = [d.strip().split(',') for d in data]
        header = data[0]
        season_info = []
        for season in data[1:]:
            season_info.append({k:v for (k,v) in zip(header, season)})      
    main(season_info[:-1])
