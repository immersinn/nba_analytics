
import datetime
import re
import sys
from nba_analytics import espngames
from nba_analytics.webpage_parse import soupypages, makePage


nba_root        = "http://scores.espn.go.com/nba/scoreboard?date="
ncaa_root       = "http://scores.espn.go.com/ncb/scoreboard?date="


root_dict       = {'NBA':nba_root,
                   'NCAM':ncaa_root,
                   }

# out of date; espn reformatted their pages 
key_phrase = re.compile(r'''var thisGame = new gameObj\("(\d{7,12})".*\)''')


def initNbaGamesFromEspn(start_date, end_date):
    """

    """
    game_ids = retrieveEspnGameIds(start_date,
                                   end_date,
                                   'NBA')
    for game_id in game_ids:
        print("Game ID: %s" % game_id)
        game = espngames.NBAGame(game_id)
        game.initFromEspn()
        game_info_dict = game.dataToDict()
        shot_data = game_info_dict.pop('shots')
        print(game_info_dict['recap'][:50])
        print(game_info_dict['game_stats']['stats']['home'])


#////////////////////////////////////////////////////////////
#{ modules for retrieveing game ids from ESPN given game dates
#////////////////////////////////////////////////////////////


def retrieveEspnGameIds(start_date, end_date, cat):
    """

    """
    try:
        root_url = root_dict[cat]
    except KeyError:
        err_msg = "Non-supported sport type entered"
        raise KeyError, err_msg
    if verifyDate(start_date) and verifyDate(end_date):
        game_ids = []
        dates = genDateSeq(start_date, end_date)
        if not dates:
            print('Start date was after end date')
        for date in dates:
            print(date)
            game_ids.extend(retrieveEspnGameIdsForDay(date, root_url))
        total_game_ids = len(game_ids)
        print("%s game ids retrieved for the dates provided" % total_game_ids)
        return game_ids


def retrieveEspnGameIdsForDay(date, root_url):
    """

    """
    url = root_url + date
    
##    url = "http://scores.espn.go.com/nba/scoreboard?date=20150202"

##    scores_page = soupypages.soupFromUrl(url)
##    if scores_page['pass']:
##        scores_page = scores_page['soup']
##        game_data = scores_page.body.findAll(id="main-container")[0].find('div', class_='scoreboards').attrs['data-data']
##        game_data = re.subn('true', "'true'", game_data)[0]
##        game_data = re.subn('false', "'false'", game_data)[0]
##        game_data = eval(game_data)
##        game_ids = [game['id'] for game in game_data['events']]
##        return game_ids

    scores_page = soupypages.soupFromUrl(url)
    if scores_page['pass']:
        scores_page = scores_page['soup']
        scripts = scores_page.head.findAll('script')
        game_data = [s for s in scripts if s.contents and s.contents[0].startswith('window.espn.scoreboardData')][0]
        game_data = re.search(r'{.*}', game_data.contents[0]).group()
        game_data = re.subn('true', '"true"', game_data)[0]
        game_data = re.subn('false', '"false"', game_data)[0]
        game_data = re.subn(r'null', '""', game_data)[0]
        game_data = game_data.split(';window.espn.scoreboardSettings')[0]
        game_data = eval(game_data)
        game_ids = [game['id'] for game in game_data['events']]
        return(game_ids)
    

    
##    scores_page = makePage(url, hdr=True)
##    if scores_page['pass']:
##        game_ids = key_phrase.findall(scores_page['page'])
##        return game_ids
    
    else:
        err_msg = scores_page['err']
        if type(err_msg) == str:
            print("Failed to retrieve scores page for %s. Error: %s" %\
                  (date, err_msg))
        else:
            print("Failed to retrieve scores page for %s. Unknown error." %\
                  date)
        return []


#////////////////////////////////////////////////////////////
#{ date stuff
#////////////////////////////////////////////////////////////


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

    
if __name__ == "__main__":
    start_date = [2014, 10, 25]
    end_date = [2015, 6, 20]
    cat = 'NBA'
    initNbaGamesFromEspn(start_date, end_date)
##    game_ids = retrieveEspnGameIds(start_date, end_date, cat)
##    print(len(game_ids))
##    print(game_ids[:10])
