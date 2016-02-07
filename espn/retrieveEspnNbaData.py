

from webpage_parse.soupypages import soupFromUrl
from parseEspnNbaPages import (espnRecapFromSoup,
                               espnBoxFromSoup,
                               espnPbpFromSoup,
                               espnShotsFromSoup)


null_value      = '&nbsp;'
CONTENT_DICT    = {'pbp':('class', 'mod-content'),
                   'box':('id', 'my-players-table')}
EXTRA_LIST      = [('class','game-time-location')]


def dataFromUrl(url, ptype, game_id):
    page = espnNbaPage(url, ptype, game_id)
    page.retrievePageData()
    return page.data


class espnNbaPage():


    def __init__(self, url, ptype, game_id):
        self.game_id = game_id
        self.url = url
        self.ptype = ptype


    def retrievePageData(self):
        if not hasattr(self, 'soup'):
            self.makeSoup()
        if self.goodSoup:
            self.extractDataFromSoup()
        else:
            print('Failed to retrieve %s for %s' %\
                  (self.ptype, self.game_id))
            self.data = {}

        
    def makeSoup(self):
        if self.ptype == 'shots':
            soup = soupFromUrl(self.url, parser='xml')
            self.goodSoup = soup['pass']
            self.soup = soup['soup']
        else:
            soup = soupFromUrl(self.url, hdr=True)
            self.goodSoup = soup['pass']
            self.soup = soup['soup']        


    def extractDataFromSoup(self):
        if self.ptype == 'ext':
            self.processExt()
        elif self.ptype == 'box':
            self.processBox()
        elif self.ptype == 'pbp':
            self.processPbp()
        elif self.ptype == 'shots':
            self.processShots()


    def processExt(self):
        data = espnRecapFromSoup(self.soup, EXTRA_LIST)
        self.data = data
##        self.data = self.soup
        

    def processBox(self):
        data = espnBoxFromSoup(self.soup,
                               CONTENT_DICT[self.ptype],
                               self.game_id)
        self.data = data
##        self.data = self.soup
        

    def processPbp(self):
        if 'Play-By-Play not available' in self.soup.text:
            data = {'head':'No PBP data for game',
                    'content':''}
        else: 
            data = espnPbpFromSoup(self.soup,
                                   CONTENT_DICT[self.ptype])
        self.data = data
##        self.data = self.soup


    def processShots(self):
        data = espnShotsFromSoup(self.soup, self.game_id)
        self.data = data
##        self.data = self.soup

