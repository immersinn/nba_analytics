
import time
import requests

import numpy as np
import pandas as pd

from dbinterface_python.dbconns import connectMon


# URL Builders

## General text strings for building urls
event_id_txt = "eventid="
game_id_txt = "gameid="
start_period_txt = "startperiod="
end_period_txt = "endperiod="


## Game Moments URL
mom_url_base = "http://stats.nba.com/stats/locations_getmoments/?"
def momUrl(event_id, game_id):
    mom_url = mom_url_base +\
              event_id_txt + str(event_id) + '&' + \
              game_id_txt + game_id
    return(mom_url)


## Game PBP URL
pbp_url_base = "http://stats.nba.com/stats/playbyplay/?startperiod=1&endperiod=10&gameid=0021400637"
def pbpUrl(start_period, end_period, game_id):
    pbp_url = pbp_url_base + \
    start_period_txt + str(start_period) + '&' + \
    end_period_txt + str(end_period) + '&' + \
    game_id_txt + game_id
    return(pbp_url)


# Helper functions / preprocessing / postprocessing

def count2Id(num):
    """
    :type num: int
    :param num: integer representing an event_id

    :rtype eid: str
    :param eid: string version of 'num' with buffer '0's
    """
    
    if num < 10:
        eid = '00' + str(num)
    elif num < 100:
        eid = '0' + str(num)
    else:
        eid = str(num)
    return(eid)


def transformMomentsMDB(raw_data, game_id, event_id):
    """
    :type raw_data: json
    :param raw_data: json file containing the moments data

    :type game_id: str
    :param game_id: ESPN Game ID for the game from which 'raw_data' is from

    :type event_id: str
    :param event_id: ESPN Moment ID for the moment from which 'raw_data' is from

    :rtype data_dict: dict
    :param data_dict: dictionary containing moment data, meta data,
                        that can be imported into MDB

    Transforms the json file extracted from the game - event page
    into a dictionary with relevant game, player info that can be
    imported into MDB.

    Partially Sourced from:
    http://savvastjortjoglou.com/nba-play-by-play-movements.html
    """
    
    # A dict containing home players data
    home = raw_data["home"]
    # A dict containig visiting players data
    away = raw_data["visitor"]
    # A list containing each moment
    moments = raw_data["moments"]
    # creates the players list with the home players
    players = home["players"]
    # Then add on the visiting players
    players.extend(away["players"])
    # Get list of player ids for players in moment
    player_ids_home = [p['playerid'] for p in home["players"]]
    player_ids_away = [p['playerid'] for p in away["players"]]
    player_ids = player_ids_home
    player_ids.extend(player_ids_away)

    # Initialize data dict for inserting into MDB
    data_dict = {'game_id' : game_id,
                 'game_date' : raw_data['gamedate'],
                 'home' : home['name'],
                 'away' : away['name'],
                 'event_id' : event_id,
                 'player_ids' : player_ids,
                 'player_ids_home' : player_ids_home,
                 'player_ids_away' : player_ids_away}

    if moments:
        moments_flag = 'True'
        # Get meta info
        quarter = raw_data['moments'][0][0]
        game_clock_start = raw_data['moments'][0][2]
        game_clock_end = raw_data['moments'][-1][2]
        shot_clock_start = raw_data['moments'][0][3]
        shot_clock_end = raw_data['moments'][-1][3]
                
        headers = ["team_id", "player_id", "x_loc", "y_loc",
                   "radius",
                   "moment", "timestamp", "game_clock", "shot_clock"]
        
        player_moments = []
        for moment in moments:
            for player in moment[5]:
                    player.extend((moments.index(moment,), moment[1],
                                   moment[2], moment[3]))
                    player_moments.append(player)
        pm_df = pd.DataFrame(player_moments, columns = headers)

        # Create dict from dataframe
        for h in headers:
            data_dict[h] = list(pm_df[h])
        data_dict['player_ids'] = player_ids

    else:
        moments_flag = 'False'
        # Assign 'None' to empty data
        quarter =  'None'
        game_clock_start = 'None'
        game_clock_end = 'None'
        shot_clock_start = 'None'
        shot_clock_end = 'None'
    
    # Finalize data dict for MDB insertion
    data_dict.update({'moments_flag' : moments_flag,
                      'quarter' : quarter,
                      'game_clock_start' : game_clock_start,
                      'game_clock_end' : game_clock_end,
                      'shot_clock_start' : shot_clock_start,
                      'shot_clock_end' : shot_clock_end})
    
    return(data_dict)



# Data Retrieval


def retrievePbpEspn(game_id):
    pbp_url = pbpUrl(start_period_id, end_period_id, game_id)
    pbp = requests.get(url)
    plays = pbp['resultSets'][0]['rowSet']
    plays = {i : v for i,v in enumerate(plays)}
    return(plays)


def retrieveMomEspn(game_id):
    """
    :type game_id: str
    :param game_id: ESPN Game ID for the game for which data is
                    to be retrieved

    :rtype: None
    :param: N/A 

    For the provided game_id, iterates over potential event_ids,
    attempts to retrieve data, converts data to a dict object using
    "transformMomentsMDB", and inserts data into NBAData.Moments
    collection upon successful retrieval.

    Current behavior halts retrieval after 3 consecutive data retrieval
    failures are encounterd, as this is assumed sufficient to indicate
    that no more moments for the current game are available.

    Currently does not perform as expected. Potential improvements:
    
    i)   Need to check into 'urllib2' instead of 'requests', fake browser
    ii)  use Tor Network via stem
    iii) change delay behavior
    """

    moments = []
    stop = False
    count = 1
    consecutive_fails = 0

    while not stop:
        print('Attempting event id %s' % count)
        attempt_count = 1
        event_id = count2Id(count)
        url = momUrl(event_id, game_id)
        data_dict = {}
        while attempt_count < 4 and not data_dict:
            response = requests.get(url)
            if response.ok:
                data_dict = transformMomentsMDB(response.json(),
                                             game_id, event_id)
            else:
                attempt_count += 1
                time.sleep(5 + 2 * attempt_count)

        # Cleanup
        count += 1
        if not data_dict:
            print('Failed to retrieve...')
            consecutive_fails += 1
        else:
            moments.append(data_dict)
            consecutive_fails = 0

        if consecutive_fails > 3:
            stop = True
        
        time.sleep(3)

    print('fine')
    return(moments)






def main():
    # Process a game
    pbp_conn = connectMon.MongoConn(db = 'NBAData', coll_name = 'PlayByPlay')
    mom_conn = connectMon.MongoConn(db = 'NBAData', coll_name = 'Moments')
    game_id = '0021400637'
    pbp = retrievePbpEspn(game_id)
    moments = retrieveMomEspn(game_id)
