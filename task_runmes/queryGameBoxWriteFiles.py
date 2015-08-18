
import sys

sys.path.append('/Users/immersinn/Gits/')
from  dbinterface_python.dbconns import connectMon


def createGameBoxInfoFile():
    out_file = '/Users/immersinn/Data/DataDumps/NBA/GameBoxInfo.csv'
    db_conn = connectMon.MongoConn({'db_name':'NBAData',
                                    'coll_name':'Games'})
    teams_cursor = db_conn.query(fields = {'game_stats.stats' : 1,
                                           'game_id' : 1,
                                           '_id' : 0},
                                 limit = 0)
    game_team_dict = {}
    for entry in teams_cursor:
        game_team_dict[entry['game_id']] = entry['game_stats']['stats']

    with open(out_file, 'w') as f1:
        header = 'GameID,Team'
        atrs = game_team_dict.values()[0]['home'].keys()
        mas = []
        for i,a in enumerate(atrs):
            if a.endswith('M-A'):
                header += ',' + a[:-3] + '-M'
                header += ',' + a[:-3] + '-A'
                mas.append(i)
            else:
                header += ',' + a
        header += '\n'
        f1.write(header)
        for k,v in game_team_dict.items():
            for t in ['home', 'away']:
                data_line = [k]
                data_line.append(t)
                for i,val in enumerate(v[t].values()):
                    if i in mas:
                        data_line.extend(val.split('-'))
                    else:
                        data_line.append(val)
                data_line = ','.join(data_line)
                data_line += '\n'
                f1.write(data_line)
    print('Game Box Info File written to %s' % out_file)


def main():
    createGameBoxInfoFile()


if __name__=="__main__":
    main()
