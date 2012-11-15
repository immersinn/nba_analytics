import sys, os

import getESPNPagesNBA
import update_players_site


def runmain2(gameids):

    '''Grab data from pages; box only'''
    box = dict()
    for gid in gameids:
        box[gid] = getESPNPagesNBA.getbox(gid)
    print 'Finished grabbing box score pages from games'''
    print 'Adding found players to players_site DB'''
    #print box[gid]['ref_pls']
    db = update_players_site.makeConn()
    with db:    # connection wasn't closing properly before...
        for key in box.keys():
            cursor = db.cursor()
            update_players_site.addPlayers(cursor, box[key]['ref_pls'])
    print 'Finsihed added all players to db'
    

if __name__=="__main__":
    # get date from cmd line
    args = sys.argv[1:]
    date = args[0]

    if date:
        print "Ret-ing games from" + date
        gameids = getESPNPagesNBA.getidswebs(date)

    if not gameids:
        msg = 'No valid game ids provided. Terminating program.'
        raise ValueError, msg
    else:
        '''If everything is OK up to this point, run the main code'''
        if runmain2(gameids):
            print "Process complete."
