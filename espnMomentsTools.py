
import time

import requests
import pandas as pd

from dbinterface_python.dbconns import connectMon


url_base = "http://stats.nba.com/stats/locations_getmoments/?"
event_txt = "eventid="
game_txt = "&gameid="



def retrieveDumpGameMoments(game_id, conn):
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

    stop = False
    count = 1
    consecutive_fails = 0

    while not stop:
        print('Attempting event id %s' % count)
        attempt_count = 1
        event_id = count2Id(count)
        url = ''.join([url_base,
                   event_txt, event_id,
                   game_txt, game_id])
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
            conn.insert(data_dict)
            consecutive_fails = 0

        if consecutive_fails > 3:
            stop = True
        
        time.sleep(3)

    print('fine')


def retrieveGameMoments(game_id):
    """
    :type game_id: str
    :param game_id: ESPN Game ID for the game for which data is
                    to be retrieved

    :rtype moments: dict
    :param moments: dictionary of moments retrieved for game_id;
                    key : value :: event_id : moments_data_dict

    For the provided game_id, iterates over potential event_ids,
    attempts to retrieve data, and stops after stopping critera
    is met.

    """

    moments = {}
    stop = False
    count = 1

    while not stop:
        print('Attempting event id %s' % count)
        attempt_count = 1
        event_id = count2Id(count)
        url = ''.join([url_base,
                   event_txt, event_id,
                   game_txt, game_id])
        try:
            response = requests.get(url)
            if response.json():
                new_data = transformMoments(response.json(),
                                            game_id, event_id) 
                movements[event_id] = response.json()
                print('Success!')
        except ValueError:
            time.sleep(2)
            print('Failed to retrieve...')
        finally:
            count += 1

    return(moments)


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
                                

def transformMomentsFull(raw_data):
    """
    :type raw_data: json
    :param raw_data: json file containing the moments data

    :rtype pm_df: pandas data frame
    :param pm_df: data frame with formatted moments data

    Transforms the json file extracted from the game - event page
    into a pandas dataframe object.

    Source: http://savvastjortjoglou.com/nba-play-by-play-movements.html
    """
    
    # A dict containing home players data
    home = raw_data["home"]
    # A dict containig visiting players data
    visitor = raw_data["visitor"]
    # A list containing each moment
    moments = raw_data["moments"]
    # creates the players list with the home players
    players = home["players"]
    # Then add on the visiting players
    players.extend(visitor["players"])
    
    headers = ["team_id", "player_id", "x_loc", "y_loc", 
           "radius", "moment", "game_clock", "shot_clock"]
    player_moments = []
    for moment in moments:
	for player in moment[5]:
		player.extend((moments.index(moment,), moment[2], moment[3]))
		player_moments.append(player)

    pm_df = pd.DataFrame(player_moments, columns = headers)

    # initialize new dictionary
    id_dict = {}

    # Add the values we want
    for player in players:
        id_dict[player['playerid']] = [player["firstname"]+" "+player["lastname"],
                                       player["jersey"]]
    # Add the value for ball
    id_dict.update({-1: ['ball', np.nan]})

    # Associate player name, jersey, id with data in pm_df
    pm_df["player_name"] = df.player_id.map(lambda x: id_dict[x][0])
    pm_df["player_jersey"] = df.player_id.map(lambda x: id_dict[x][1])

    return(pm_df)


def momentsMDB2PDDF(mdb_moments):
    """
    :type mdb_moments: dict
    :param mdb_moments: dictionary representation of a single moment's
                        data as retrieved from MDB

    :rtype pm_df: pandas DataFrame
    :param pm_df: pd.DataFram  representation of input moment's data

    Transform moments data as stored in MDB to pandas DF
    """
    
    headers = ["team_id", "player_id", "x_loc", "y_loc", 
           "radius", "moment", "game_clock", "shot_clock"]
    pm_df = pd.DataFrame()
    for h in headers:
	pm_df[h] = mdb_moments[h]
    return(pm_df)


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


def getMomentDF(game_id, event_id):

    mc = connectMon.MongoConn(db_name='NBAData', coll_name = 'Moments')
    game_id = "0041400235" if not game_id else game_id

    ret = mc.query(spec = {'game_id' : game_id,
                           'event_id' : event_id},
                   limit = 1)
    mom = ret.next()
    df = momentsMDB2PDDF(mom)
    return(df)
    


def main():
    game_id = "0041400235"
    mc = connectMon.MongoConn()
    db_name = 'NBAData'
    coll_name = 'Moments'
    mc.makeDBConn(db_name)
    mc.makeCollConn(coll_name)
    retrieveDumpGameMoments(game_id, mc)


if __name__=="__main__":
    main()
        
