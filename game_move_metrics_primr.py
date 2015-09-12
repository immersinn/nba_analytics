
import numpy as np
import scipy as scpy
from scipy.spatial.distance import euclidean
import pandas as pd
import matplotlib.pyplot as plt



"""
Sourced from: http://savvastjortjoglou.com/nba-play-by-play-movements.html
"""

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


def distP2P(player_a, player_b):
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


def ballPlayerDists(df):
    """
    :type df: pandas DataFram
    :param df: DataFrame containing the moments player and ball data

    :rtype ball_distances: pandas DataFram
    :rparam ball_distances: DataFrame containing distance of each player
                            from ball at each moments. Columns are an
                            individual player's data
    """

    player_ids = list(pd.unique(df.player_id))
    player_ids.remove(-1)
    ball_df = playerLoc(df, -1)
    ball_distances = pd.DataFrame()

    for pid in player_ids:
        player_df = playerLoc(df, pid)
        dist = distP2P(ball_df, player_df)
        ball_distances[pid] = dist

    return(ball_distances)


def pairwisePlayerDists(df):
    
    player_ids = list(pd.unique(df.player_id))
    player_ids.remove(-1)

    distances = {}
    for i, pid_a in enumerate(player_ids):
        player_a = playerLoc(df, pid_a)
        for j, pid_b in enumerate(player_ids[i+1:]):
            player_b = playerLoc(df, pid_b)
            dist = distP2P(player_a, player_b)
            distances[pid_a][pid_b] = dist
            distances[pid_b][pid_a] = dist

    return(distances)


def ballEvents(df):
    """
    Determine where passes, steals, and shots occur in the data
    """
    pass


def ballPass(df):
    """
    What does a pass (non-handoff) look like?

    player_a and player_b are distance x from one another.
    balll starts in player_a posession,
    and some small distance from player_a.
    Ends in player_b posession; distance of ball from original.

    Pair of players whose distance to the ball changes at approx
    the same rate, but different sign
    
    """



def posessBall(pm_df):
    """
    Determine which player has the ball.  If ambguous, mark as such.

    Check min ball distance to players; if < zzz, and only player, than
    that player has ball.

    If multi players within threshold, then it's ambigious

    If no players winthin threshold, then no one has ball (free ball,
    shot, pass)
    """
    ball_distances = ballPlayerDists(pm_df)
    min_ball_dists = ball_distances.min(axis = 1)

    cutoff = 2.5
    ltcut = ball_distances < cutoff
    player_ids = list(player_ids)
    
    posession = []
    for i in range(ltcut.shape[0]):
	pos = np.where(ltcut.irow(i))[0]
	if len(pos) == 0:
		posession.append('fb')
	elif len(pos) == 1:
		posession.append(str(player_ids[pos[0]]))
	else:
		posession.append('ambig')


def playerBallDistPlot(pm_df):
    ball_dists = ballPlayerDists(pm_df)
    labels = list(ball_dists.columns)

    plt.figure(figsize=(12,9))
    for i,pid in enumerate(labels):
##        plt.plot(pm_df.shot_clock.unique(), dist)
        plt.plot(pm_df.moment.unique(), ball_distances[pid])

        y_pos = dist[-1]
    
        plt.text(6.15, y_pos, labels[i], fontsize=14)
        plt.grid(axis='y',color='gray', linestyle='--', lw=0.5, alpha=0.5)
        plt.show()
    
