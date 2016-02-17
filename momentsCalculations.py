

import numpy as np
from scipy.spatial.distance import euclidean
import pandas


def determineBallTransitions(df, pids,
                             poss=list()):


    indx_map = list(range(0,df.shape[0],11))
    if not poss:
        poss = determineBallPosessions(df, pids)
    
    from_list = []
    to_list = []
    start_time = []
    end_time = []
    start_pass = []
    end_pass = []

    from_player = ''
    indx = 0
    while not from_player:
        if poss[indx]:
            from_player = poss[indx]
        else:
            indx += 1

    start_indx = indx
    while indx < len(poss):
        if poss[indx]:
            if from_player != poss[indx]:
                end_indx = indx
                to_player = poss[indx]
                
                from_list.append(from_player)
                to_list.append(to_player)
                start_pass.append(start_indx)
                end_pass.append(end_indx)
                start_time.append(df.game_clock[indx_map[start_indx]])
                end_time.append(df.game_clock[indx_map[end_indx]])
                
                from_player = to_player

                start_indx = end_indx
            else:
                start_indx += 1
                indx += 1
        else:
            if not start_indx:
                start_indx = indx
            indx += 1
                
    pos_ft = pandas.DataFrame(data = {'FromPlayer' : from_list,
                                      'ToPlayer' : to_list,
                                      'StartGameClock' : start_time,
                                      'EndGameClock' : end_time,
                                      'StartIndx' : start_pass,
                                      'EndIndx' : end_pass})
    return(pos_ft)



def determineBallPosessions(df, pids,
                           max_dist=3, max_radius=5):

    indx_map = list(range(0,df.shape[0],11))
    pbd = ballPlayerDists(df, pids)
    radius = df.radius[indx_map]

    # Helper funcs
    f = lambda x, y: True if x and y else False
    g = lambda x: x[0] if len(x) == 1 else int()
    h = lambda x, y: x if x and y else None

    cp = pbd < max_dist
    rt = radius < max_radius
    wp = [g(cp.columns[cp.ix[i,]]) for i in range(cp.shape[0])]
    p = [h(w,r) for (w,r) in zip(wp, rt)]

    for i in range(1, len(p)-1):
        if p[i]:
            if not p[i-1] and not p[i+1]:
                p[i] = None

    return(p)



def travelDist(player_locations):
    # get the differences for each column
    diff = np.diff(player_locations, axis=0)
    # square the differences and add them,
    # then get the square root of that sum
    dist = np.sqrt((diff ** 2).sum(axis=1))
    # Then return the sum of all the distances
    return dist.sum()


def avgSpeed(df, player_dist, units='fps'):
    # get the number of seconds for the play
    seconds = df.game_clock.max() - df.game_clock.min()
    # feet per second
    player_fps = player_dist / seconds
    # return requested data
    if units=='fps':
        return(player_fps)
    elif units=='mph':
        # convert to miles per hour
        player_mph = 0.681818 * player_fps
        return(player_mph)


def playerDF(df, player, param='pid'):

    if param == 'player':
        player_df = df[df.player_name==player]
    elif param == 'pid':
        player_df = df[df.player_id==player]
        
    return(player_df)


def playerLoc(df, player, param='pid'):

    if param == 'player':
        player_loc = df[df.player_name==player][["x_loc", "y_loc"]]
    elif param == 'pid':
        player_loc = df[df.player_id==player][["x_loc", "y_loc"]]
        
    return(player_loc)


def p2pDist(player_a, player_b):
    """
    :type player_a: pandas DataFrame
    :param player_a: subset of data from a moment specific to a player,
                     in this case "player a"

    :type player_b: pandas DataFrame
    :param player_b: subset of data from a moment specific to a player,
                     in this case "player b"

    :rtype distances: list
    :param distances: euclid dist between player a and player b for each
                      timestamp in the data
    
    Function to find the distance between players at each moment
    """

    distances = [euclidean(player_a.iloc[i], player_b.iloc[i])
                 for i in range(len(player_a))]
    return(distances)



def pairwisePlayerDists(df):
    
    player_ids = list(pd.unique(df.player_id))
    player_ids.remove(-1)

    distances = {}
    for i, pid_a in enumerate(player_ids):
        player_a = playerLoc(df, pid_a)
        for j, pid_b in enumerate(player_ids[i+1:]):
            player_b = playerLoc(df, pid_b)
            dist = p2pDist(player_a, player_b)
            distances[pid_a][pid_b] = dist
            distances[pid_b][pid_a] = dist

    return(distances)


def calcP2PDist(df, pid1, pid2):
    player_a = playerLoc(df, pid1)
    player_b = playerLoc(df, pid2)
    dist =  p2pDist(player_a, player_b)
    return(dist)



def ballPlayerDists(df, player_ids):
    """
    :type df: pandas DataFram
    :param df: DataFrame containing the moments player and ball data

    :rtype ball_distances: pandas DataFram
    :rparam ball_distances: DataFrame containing distance of each player
                            from ball at each moments. Columns are an
                            individual player's data
    """

    
##    player_ids = list(pd.unique(df.player_id))
    player_ids.remove(-1)
    ball_df = playerLoc(df, -1)
    ball_distances = pandas.DataFrame()

    for pid in player_ids:
        player_df = playerLoc(df, pid)
        dist = p2pDist(ball_df, player_df)
        ball_distances[pid] = dist

    return(ball_distances)


