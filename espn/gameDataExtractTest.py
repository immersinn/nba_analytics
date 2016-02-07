import sys
sys.path.append('/Users/immersinn/Gits/')
from nba_analytics import espngames
from nba_analytics.parseESPNPages import espnBoxFromSoup
empty_str_filter = lambda x: x not in ['', '\xc2\xa0'] # not needed normally?
gameId = '400579075'
game = espngames.NBAGame(gameId)
game.retrieveGameData()
CONTENT_DICT    = {'pbp':('class', 'mod-content'),
                   'box':('id', 'my-players-table')}

# Test box score data extraction
ptype = 'box'
labels = CONTENT_DICT[ptype]
soup = game.box_score
player_info, game_info = espnBoxFromSoup(soup, labels, game_id)

# Test play-by-play data extraction
ptype = 'pbp'
labels = CONTENT_DICT[ptype]
soup = game.play_by_play
