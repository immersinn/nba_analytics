import sys
sys.path.append('/Users/immersinn/Gits/')
from nba_analytics import espngames
gameId = '400579075'
game = espngames.NBAGame(gameId)
game.retrieveGameData()
CONTENT_DICT    = {'pbp':('class', 'mod-content'),
                   'box':('id', 'my-players-table')}
pytpe = 'box'
labels = CONTENT_DICT[pytpe]
soup = game.box_score
tables  = soup.find_all('div', {labels[0]:labels[1]})
summary     = tables[0].findAll('tr')
details = []
content = []
for line in summary:
    details.append([str(h.text.encode('utf8')) for h in line.findAll('th')])
    content.append([str(h.text.encode('utf8')) for h in line.findAll('td')])
