

import datetime
import re
import sys
from nba_analytics import espngames
from nba_analytics.webpage_parse import soupypages, makePage
from dbinterface_python.dbconns import connectMon


def createAndReturnNbaMdbs():
    db_name = 'NBASD'
    game_coll_name = 'Games'
    mome_coll_name = 'Moments'
    gamemdb = connectMon.MongoConn(db_name=db_name,
                                   coll_name=game_coll_name)
    momemdb = connectMon.MongoConn(db_name=db_name,
                                   coll_name=mome_coll_name)

    return {'games':gamemdb,
            'moments':momemdb}


def retrieveEspnGameIdsForDay(url):

    page = soupypages.soupFromUrl(url)
    
    if page['pass']:
        gid_info = page['soup'].find('div', id='nbaSSOuter')
        game_divs = gid_info.findAll('div', class_="Recap GameLine")
        game_ids = [gd['id'] for gd in game_divs]
        game_ids = [gid.strip('nbaGL') for gid in game_ids]
        return(game_ids)
    else:
        err_msg = scores_page['err']
        if type(err_msg) == str:
            print("Failed to retrieve scores page for %s. Error: %s" %\
                  (date, err_msg))
        else:
            print("Failed to retrieve scores page for %s. Unknown error." %\
                  date)
        return []


def verifyDate(date):
    """
    Checks to make sure provided date is valid format, in past or now.
    Format expected is YYYYMMDD
    """
    today = datetime.date.today()
    date = datetime.date(date[0], date[1], date[2])
    if date <= today:
        return True
    else:
        print "WARNING: future date provided; this isn't a crystal ball!!"
        return False
    

def genDateSeq(start_date, end_date):
    """
    :type start_date: list
    :param start_date: initial date desired in date sequence;
    [YYYY, M, D], all integers

    :type end_date: list
    :param end_date: final date desired in date sequence;
    [YYYY, M, D], all integers

    :rtype: list
    
    Generates a sequence of dates in the YYYYMMDD format
    """
    dates = []
    start = datetime.date(start_date[0], start_date[1], start_date[2])
    end = datetime.date(end_date[0], end_date[1], end_date[2])
    step = datetime.timedelta(days=1)
    while start <= end:
        dates.append(start.strftime('%Y%m%d'))
        start += step
    return dates


def main():

    """
    Tuesday, October 28, 2008, and ended on Wednesday, April 15, 2009.
    The 2009 NBA Playoffs started on Saturday, April 18, 2009 and ran
    until Sunday, June 14

    example url: url = "http://www.nba.com/gameline/20150209/"
    """
 
    which_data_list = ['moments', 'play_by_play',
                       'player_stats_adv', 'team_stats_adv', 'game_stats',
                       'season', 'date']
         
    start_date = [2014, 10, 25]
    end_date = [2015, 6, 20]
    dates = genDateSeq(start_date, end_date)
    root_url = 'http://www.nba.com/gameline/'
    dbs = createAndReturnNbaMdbs()
    games = dbs['games']
    moments = dbs['moments']
    
    for date in dates:
        if int(date) < 20150418:
            season = '20142015Regular'
        elif int(date) < 20150604:
            season = '20142015Playoffs'
        else:
            season = '20142015Finals'

        game_ids = retrieveEspnGameIdsForDay(root_url + date)

        for game_id in game_ids:
            print("Game ID: %s" % game_id)
            game = espngames.NBAStatsGame(game_id,
                                          season = season,
                                          date = date)
            game.initFromEspn()
            game_info_dict = game.dataToDict(which_data = which_data_list)

            try:
                moments_info_list = game_info_dict.pop('moments')
                if moments_info_list:
                    moments.insert(moments_info_list)
                else:
                    print('Empty moments data for game %s' % game_id)
            except KeyError:
                print('No moments data for game %s' % game_id)
            games.insert(game_info_dict)


if __name__=="__main__":
    main()

    
