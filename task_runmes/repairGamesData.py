
from dbinterface_python.dbconns import connectMon
from nba_analytics import espnNbaDataExtraction


def updateGame(conn, game):
    game_id = game['game_id']
    print('Updating game %s' % game_id)

    try:
        new_box = espnNbaDataExtraction.retrieveBoxEspn(game_id)
        conn.update({'game_id' : game_id},
                     content_key = "player_stats_adv",
                     new_content = new_box['player_stats'])
        conn.update({'game_id' : game_id},
                     content_key = "team_stats_adv",
                     new_content = new_box['team_stats'])
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception as X:
        print('caught: ' + str(X.__class__) + '; message: ' + X.message)
    


def main():
    conn = connectMon.MongoConn(db_name='NBASD',
                                coll_name='Games')
    results = conn.query(limit = 0,
                             fields = {'game_id' : True})
    for r in results:
        updateGame(conn, r)


if __name__ == '__main__':
    main()
