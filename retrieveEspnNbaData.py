

from webpage_parse.soupypages import soupFromUrl


null_value      = '&nbsp;'
CONTENT_DICT    = {'pbp':('class', 'mod-content'),
                   'box':('id', 'my-players-table')}
EXTRA_LIST      = [('class','game-time-location')]


def dataFromUrl(url, ptype):
    page = espnNbaPage(url, ptype)
    page.retrievePageData()
    return page.data


class espnNbaPage():


    def __init__(self, url, ptype):
        self.url = url
        self.ptype = ptype


    def retrievePageData(self):
        if not hasattr(self, 'soup'):
            self.makeSoup()
        self.extractDataFromSoup()

        
    def makeSoup(self):
        if self.ptype == 'shots':
            self.soup = soupFromUrl(url, parser='xml')['soup']
        else:
            self.soup = soupFromUrl(self.url, hdr=True)['soup']


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
        data = getEspnExt(self.soup, EXTRA_LIST)
        self.data = data
        

    def processBox(self):
        labels  = CONTENT_DICT[ptype]
        tables  = self.soup.find_all('div',
                                     {labels[0]:labels[1]})
        data = getEspnBox(tables[0])
        self.data = data
        

    def processPbp(self):
        labels  = CONTENT_DICT[ptype]
        if 'Play-By-Play not available' in self.soup.text:
            data = {'head':'No PBP data for game',
                    'content':''}
        else: 
            tables = self.soup.find_all('div',
                                        {labels[0]:labels[1]})
            data = getEspnPbp(tables[1])     # check this plz
        self.data = data


    def processShots(self):
        data = getEspnShots(self.soup)
        self.data = data

