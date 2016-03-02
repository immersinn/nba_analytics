from nba_analytics import fileHelper
from nba_analytics import nbaGame


gid = '0041400161'
raw_moments, raw_pbp = fileHelper.loadFiles()
pbp01 = [p for p in raw_pbp if p['game_id']==gid][0]
game_info = {'game_id' : pbp01['game_id'],
             'player_stats_adv' : pbp01['player_stats_adv'],
             'team_stats_adv' : pbp01['team_stats_adv'],
             'game_stats' : pbp01['game_stats']}
pbp_info = pbp01['play_by_play']
moments_info = [m for m in raw_moments if m['game_id']==gid]

ge = nbaGame.GameEvents(game_info, pbp_info)
ge.preprocess()
gm = nbaGame.GameMoments(game_info, moments_info)
gm.preprocess()
gs = nbaGame.GameSegments(game_info, gm, ge)
