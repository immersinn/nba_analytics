
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


def selectiveQueryandWrite():

    out_file = '/home/immersinn/Data/DataDumps/NBA/MultiSeasonGameBoxInfo.csv'

    seasons = ['2008-2009 Regular', '2008-2009 Playoffs',
               '2009-2010 Regular', '2009-2010 Playoffs',
               '2010-2011 Regular', '2010-2011 Playoffs',
               '2011-2012 Regular', '2011-2012 Playoffs',]
    
    # Get game ids of interest
    db_conn = connectMon.MongoConn({'db_name':'NBAData',
                                    'coll_name':'Games'})
    teams_cursor = db_conn.query(spec = {'season' : {'$in' : seasons}},
                                 fields = {'game_stats.teams' : 1,
                                           'game_id' : 1,
                                           'season' : 1,
                                           '_id' : 0},
                                 limit = 0)
    game_ids = [entry['game_id'] for entry in teams_cursor if entry['game_stats']]

    db_conn = connectMon.MongoConn({'db_name':'NBAData',
                                    'coll_name':'Games'})


    # Query game data for game ids of interest
    with open(out_file, 'w') as f1:
        header = 'GameID,Team'
        atrs = []

        for gid in game_ids:
            teams_cursor = db_conn.query(spec = {'game_id' : gid},
                                         fields = {'game_stats.stats' : 1,
                                                   'game_id' : 1,
                                                   '_id' : 0},
                                         limit = 0,
                                         verbose = False)
            if teams_cursor.count(with_limit_and_skip=True) == 1:
                game = teams_cursor.next()
                if not atrs:
                    atrs = game['game_stats']['stats']['home'].keys()
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

                for t in ['home', 'away']:
                    data_line = [game['game_id']]
                    data_line.append(t)
                    for i,val in enumerate(game['game_stats']['stats'][t].values()):
                        if i in mas:
                            data_line.extend(val.split('-'))
                        else:
                            data_line.append(val)
                    data_line = ','.join(data_line)
                    data_line += '\n'
                    f1.write(data_line)
                    
            else:
                for t in ['home', 'away']:
                    data_line = [gid]
                    data_line.append(t)
                    data_line.extend([',' for _ in range(len(header) - 2)])
                    data_line = ''.join(data_line)
                    data_line += '\n'
                    f1.write(data_line)

    print('Game Box Info File written to %s' % out_file)
      
        


def main():
    createGameBoxInfoFile()


if __name__=="__main__":
    selectiveQueryandWrite()
