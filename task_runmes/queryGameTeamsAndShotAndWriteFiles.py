
import sys

sys.path.append('/Users/immersinn/Gits/')
from  dbinterface_python.dbconns import connectMon


def createGameTeamInfoFile():
    out_file = '/Users/immersinn/Data/DataDumps/NBA/GameTeamInfo.csv'
    db_conn = connectMon.MongoConn({'db_name':'NBAData',
                                    'coll_name':'Games'})
    teams_cursor = db_conn.query(fields = {'game_stats.teams' : 1,
                                           'game_id' : 1,
                                           '_id' : 0},
                                 limit = 0)
    game_team_dict = {}
    for entry in teams_cursor:
        game_team_dict[entry['game_id']] = entry['game_stats']['teams']

    with open(out_file, 'w') as f1:
        header = 'game_id,home,away\n'
        f1.write(header)
        for k,v in game_team_dict.items():
            data_line = [k]
            data_line.extend(v.values())
            data_line = ','.join(data_line)
            data_line += '\n'
            f1.write(data_line)
    print('Game-Team File written to %s' % out_file)


def createShotInfoFile():
    out_file = '/Users/immersinn/Data/DataDumps/NBA/ShotsInfo.csv'
    shots = connectMon.MongoConn({'db_name':'NBAData',
                                  'coll_name':'Shots'})
    limit = 0
    shots_cursor = shots.query(limit=limit)
    with open(out_file, 'w') as f1:
        header = ''
        for sd in shots_cursor:
            if not header:
                sd.pop('_id')
                header = ','.join(sd.keys())
                header += '\n'
                f1.write(header)
                data_line = ','.join(sd.values())
                data_line += '\n'
                f1.write(data_line)
            else:
                sd.pop('_id')
                data_line = ','.join(sd.values())
                data_line += '\n'
                f1.write(data_line)
    print('Shots File written to %s' % out_file)


def main():
    createGameTeamInfoFile()
    createShotInfoFile()


if __name__=="__main__":
    main()
