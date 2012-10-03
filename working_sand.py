import sys, os
from BeautifulSoup import bs4 as bs
import prepworkURL

url_roster = "http://espn.go.com/nfl/team/roster/_/name/ne/order/true/new-england-patriots"
page_roster = urllib2.urlopen(url_roster).read()

soup_roster = prepworkURL.makeSoup(prepworkURL.makePage(url_roster), url_roster)
table = soup_roster.findAll('tr')
table_href = [t for t in table if str(t.a).find('href')>-1]
table_player_href = [t for t in table_href if str(t.a).find('player')>=0]
[t.a.text for t in table_player_href]
