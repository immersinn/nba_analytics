
import datetime
import re

import espngames


nba_root        = "http://scores.espn.go.com/nba/scoreboard?date="
ncaa_root       = "http://scores.espn.go.com/ncb/scoreboard?date="


root_dict       = {'NBA':nba_root,
                   'NCAM':ncaa_root,
                   }

key_phrase = re.compile(r'''var thisGame = new gameObj\("(\d{7,12})".*\)''')


def initNbaGamesFromEspn(date_range):
    """

    """
    game_ids = retrieveEspnGameIds(date_range,
                                   'NBA')
    for game_id in game_ids:
        game = espngames.NBAGame(game_id)
        game.initFromEspn()
        game_info_dict = game.dataToDict()
        shot_data = game_info_dict.pop('shots')


#////////////////////////////////////////////////////////////
#{ modules for retrieveing game ids from ESPN given game dates
#////////////////////////////////////////////////////////////


def retrieveEspnGameIds(date_range, cat):
    """

    """
    pass


def retrieveEspnGameIdsForDay(date, root_url):
    """

    """
    pass


def verifydate(date):
    """
    Checks to make sure provided date is valid format, in past or now.
    Format expected is YYYYMMDD
    """
    now = datetime.datetime.now()
    now = int(str(now.year)+\
               ('0' if now.month<10 else '') + \
               str(now.month)+\
               ('0' if now.day<10 else '') + \
               str(now.day))
    if len(date) != 8:
        print 'WARNING: non-valid date or date in invalid format'
    try:
        if int(date) <= now:
            return True
        else:
            print "WARNING: future date provided; this isn't a crystal ball!!"
            return False
    except ValueError:
        print('non-valid date or date in invalid format: %d' % date)
