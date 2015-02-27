

import sys

sys.path.append('/Users/immersinn/Gits/')

from  nba_analytics.dbconns import connectMon


def main():
    out_file = '/Users/immersinn/Data/DataDumps/NBA/Shots_test.csv'
    shots = connectMon.MongoConn({'db_name':'NBAData',
                                  'coll_name':'Shots'})
    limit = 0
    shots.query(limit=limit)
    with open(out_file, 'w') as f1:
        header = ''
        for sd in shots.LastQ:
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
    print('File written to %s' % out_file)


if __name__=="__main__":
    main()
