
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
    
