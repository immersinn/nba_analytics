
import pickle
from pandas import read_pickle

from dataFieldNames import *


def loadFiles():
    # [u'0041400161', u'0041400163', u'0041400164', u'0021400648']

    try:
        with open('/home/immersinn/Data/DataDumps/NBA/momentsSubset02.pkl', 'r') as f1:
            moments = pickle.load(f1)
    except TypeError:
        moments = read_pickle('/home/immersinn/Data/DataDumps/NBA/momentsSubset.pkl')
            
    with open('/home/immersinn/Data/DataDumps/NBA/pbpSubset02.pkl', 'r') as f1:
        pbp = pickle.load(f1)

    return(moments, pbp)


def grabGameFromLoad(gid = '0041400161'):
    """

    returns:
        moments : list of dicts
        pbp : pbp DataFrame
    """
    # Load data
    mom_list, pbp_list = loadFiles()

    # Preprocess
    ## None...pass raw out..


    # Retrieve data for specified game
    moments = [m for m in mom_list if m['game_id'] == gid]
    pbp = [p for p in pbp_list if p['game_id'] == gid] 

    return(moments, pbp)


def main():

    moments, pbp = loadFiles()
    gids = set([g for (g, _, _) in moments])
    mom_dict = {}
    for gid in gids:
        mom_dict[gid] = [(g, e, d) for (g, e, d) in moments if g == gid]
    pbp_dict = {}
    for p in pbp:
        pbp_dict[p['game_id']] = p['play_by_play']

    return(pbp_dict, mom_dict)
