
import sys

#sys.path.append('/Users/immersinn/Gits/')
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


def selectiveQuery():

    game_out_file = '/home/immersinn/Data/DataDumps/NBA/MultiSeasonGameTeamInfo.csv'
    shot_out_file = '/home/immersinn/Data/DataDumps/NBA/MultiSeasonShotsInfo.csv'
    

    seasons = ['2008-2009 Regular', '2008-2009 Playoffs',
               '2009-2010 Regular', '2009-2010 Playoffs',
               '2010-2011 Regular', '2010-2011 Playoffs',
               '2011-2012 Regular', '2011-2012 Playoffs',]
    game_ids = []


    # Query for games in seasons specified and write game info from
    # these games to a file
    db_conn = connectMon.MongoConn({'db_name':'NBAData',
                                    'coll_name':'Games'})
    
    teams_cursor = db_conn.query(spec = {'season' : {'$in' : seasons}},
                                 fields = {'game_stats.teams' : 1,
                                           'game_id' : 1,
                                           'season' : 1,
                                           '_id' : 0},
                                 limit = 0)

    with open(game_out_file, 'w') as f1:
        header = 'game_id,season,home,away\n'
        f1.write(header)
        for entry in teams_cursor:
            if entry['game_stats']:
                game_ids.append(entry['game_id'])
                data_line = [entry['game_id'],
                             entry['season'],
                             entry['game_stats']['teams']['home'],
                             entry['game_stats']['teams']['away']]
                data_line = ','.join(data_line)
                data_line += '\n'
                f1.write(data_line)
    print('Game-Team File written to %s' % game_out_file)


    # Use 'game_ids' from above to query ShotInfo corresponding to the
    # games in question
    shots = connectMon.MongoConn({'db_name':'NBAData',
                                  'coll_name':'Shots'})

    names = ['game_id', 'pts', 'made', 't', 'y', 'x', 'shot_id']
    header = ','.join(names)
    
    with open(shot_out_file, 'w') as f1:
        f1.write(header)
        for gid in game_ids:
            shots_cursor = shots.query(spec = {'game_id' : gid},
                                       fields = {'_id' : 0,
                                                 'game_id' : 1,
                                                 'pts' : 1,
                                                 'made' : 1,
                                                 't' : 1,
                                                 'y' : 1, 'x' : 1,
                                                 'shot_id' : 1},
                                       limit = 0)
            for sd in shots_cursor:
                data_line = ','.join([str(sd[n]) for n in names])
                data_line += '\n'
                f1.write(data_line)
    print('Shots File written to %s' % shot_out_file)
                   


def main():
    createGameTeamInfoFile()
    createShotInfoFile()


if __name__=="__main__":
    selectiveQuery()
