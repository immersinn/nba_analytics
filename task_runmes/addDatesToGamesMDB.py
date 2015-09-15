
import sys

from nba_analytics import espngames
from dbinterface_python.dbconns import connectMon

game_mc = connectMon.MongoCon(db_name = 'NBAData',
                                coll_name = 'Games')
game_iter = game_mc.query(specs = {},
                          fields = {'game_id' : True})
