import sys, os

import pymongo

sys.path.append('/home/immersinn/Gits/Helper-Code/Python27')
import picklingIsEasy

# set file names to use
pbp_n = '/home/immersinn/Gits/NBA-Data-Stuff/pbp_20111215to20111221.pkl'
sht_n = '/home/immersinn/Gits/NBA-Data-Stuff/sht_20111215to20111221.pkl'
# unpickle data
pbp = picklingIsEasy.unpickledata(pbp_n)
sht = picklingIsEasy.unpickledata(sht_n)

# Connect and deposit
conn = pymongo.Connection()
db = conn.NBA
sht_db = db.Reg20112012.shots
pbp_db = db.Reg20112012.pbp

for game in sht.values():
    m_id = sht_db.insert(game)

for game in pbp.values():
    m_id = pbp_db.insert(newG)
