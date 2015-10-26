
import pickle


header = ["GAME_ID",
          "EVENTNUM",
          "EVENTMSGTYPE",
          "EVENTMSGACTIONTYPE",
          "PERIOD",
          "WCTIMESTRING",
          "PCTIMESTRING",
          "HOMEDESCRIPTION",
          "NEUTRALDESCRIPTION",
          "VISITORDESCRIPTION",
          "SCORE",
          "SCOREMARGIN"]


EVENTS_LIST = ['pass',
               'steal',
               'rebound',
               'block',
               'foul',
               'shot',
               'turnover',
               'sub']


def loadFiles():
    # [u'0041400161', u'0041400163', u'0041400164', u'0021400648']

    try:
        with open('/home/immersinn/Data/DataDumps/NBA/momentsSubset.pkl', 'r') as f1:
            moments = pickle.load(f1)
    except TypeError:
        moments = pandas.read_pickle('/home/immersinn/Data/DataDumps/NBA/momentsSubset.pkl')
            
    with open('/home/immersinn/Data/DataDumps/NBA/pbpSubset.pkl', 'r') as f1:
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
##    mom_list = [{'game_id' : g,
##                 'event_id' : e,
##                 'data' : d} \
##                for (g, e, d) in mom_list]
    pbp_list = [{'game_id' : g['game_id'],
                 'play_by_play' : g['play_by_play'],
                 'player_info' : g['player_stats_adv']} \
                for g in pbp_list]

    # Retrieve data for specified game
    moments = [(g, e, d) for (g, e, d) in mom_list if g == gid]
    pbp = [p for p in pbp_list if p['game_id'] == gid][0]   

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
