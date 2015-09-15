

from nba_analytics.espnMomentsTools import retrieveDumpGameMoments
from dbinterface_python.dbconns import connectMon

start_gid = '0021400001'
end_reg_gid = '0021401230'
start_fin_gid = '0041400101'
# interesting; series are started 10 apart; consecutive within a series
# annoying because not all in 1-10 sequence will be used.  skip smartly.
# none will be above 7
end_fin_gid = '0041400406' # i.e. the finals series finished in 6 games


if __name__=="__main__":

    game_conn = connectMon.MongoConn(db_name = 'NBAData',
                                     coll_name = 'Games')
    mome_conn = connectMon.MongoConn(db_name = 'NBAData',
                                     coll_name = 'Moments')

    # Populate the 2014 - 2015 Season for the moment
    curr_games = game_conn.query(spec = {'season' : \
                                         {'$in' : ['20142015Regular',
                                                   '20142015Playoffs']}},
                                 fields = {'game_id' : True})

    for game in curr_games:
        gid = game['game_id']
        print('Retrieveing data for game id %s' % gid)
        retrieveDumpGameMoments(gid, mome_conn)
        print('Completed extracting moments')
