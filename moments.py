
import numpy
import scipy
from scipy.spatial.distance import euclidean
import pandas


class GameMoments(object):

    def __init__(self,):
        pass


class GameGraphMoment(object):


    def __init__(self, data, meta):
        self.assignData(data)
        self.assignMeta(meta)


    def assignData(self, data):
        self.data = data


    def assignMeta(self, meta):
        self.meta = meta


    def genPosChain(self, xy_cutoff=3, rad_cutoff=5):
        bpc = ballPosessionChain(self.data,
                                 xy_cutoff, rad_cutoff)
        self.pcdf = buildBallTransDf(bpc,
                                     self.data.game_clock)


    def getPosChangeEvents(self,):
        if 'pcdf' not in self.__dict__.keys():
            self.genPosChain()
        pc_dict = self.pcdf.to_dict()
        pc_events = [{'from' : f, 'to' : t, 'gc' : c} \
                     for (f, t, c) in zip(pc_dict['From'].values(),
                                          pc_dict['To'].values(),
                                          pc_dict['GameClock'].values(),)]
        return(pc_events)    



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

    player_ids = list(pandas.unique(df.player_id))
    player_ids.remove(-1)
    ball_df = playerLoc(df, -1)
    ball_distances = pandas.DataFrame()

    for pid in player_ids:
        player_df = playerLoc(df, pid)
        dist = distP2P(ball_df, player_df)
        ball_distances[pid] = dist

    return(ball_distances)


def pairwisePlayerDists(df):
    
    player_ids = list(pandas.unique(df.player_id))
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


def ballPosessionChain(seg, xy_cutoff=3, rad_cutoff=5):

    ##############
    pbd = ballPlayerDists(seg)
    
    posession_test = pbd <= xy_cutoff
    radius = seg.radius[range(0, 11*len(pbd), 11)]
    
    which_player = [list(posession_test.columns[posession_test.ix[i]]) \
                    for i in posession_test.index]
    
    f = lambda x, y: True if x and y else False
    g = lambda x: x[0] if len(x) == 1 else int()
    
    close_player = [g(cp) for cp in which_player]
    has_player = [f(cp, rtv < rad_cutoff) for (cp, rtv) in zip(close_player, radius)]
    adj_match = [a == b and b for (a, b) in zip(close_player[:-1], close_player[1:])]
    ###############

    
    if has_player[0]:
        player_pos_chain = [which_player[0][0]]
    else:
        player_pos_chain = [None]

    for i, hp in enumerate(has_player[1:]):
        if hp:
            player_pos_chain.append(which_player[i + 1][0])
        else:
            player_pos_chain.append(None)
            
    return(player_pos_chain)



def buildBallTransDf(player_pos_chain, game_clock):
    
    # Determine which ball transitions happen between players
    # during the game using the player_pos_stream
    from_list = []
    to_list = []
    time_list = []

    from_player = ''
    indx = 0
    while not from_player:
        if player_pos_chain[indx]:
            from_player = player_pos_chain[indx]
        else:
            indx += 1

    while indx < len(player_pos_chain):
        if player_pos_chain[indx]:
            if from_player != player_pos_chain[indx]:
                to_player = player_pos_chain[indx]
                #from_list.append(rev_pid_lookup[from_player])
                #to_list.append(rev_pid_lookup[to_player])
                from_list.append(from_player)
                to_list.append(to_player)
                time_list.append(game_clock[11*indx])
                from_player = to_player
            else:
                indx += 1
        else:
            indx += 1

    pos_ft = pandas.DataFrame(data = zip(from_list, to_list, time_list),
                              columns = ['From', 'To', 'GameClock'])
    return(pos_ft)
