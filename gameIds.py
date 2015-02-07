

def getidsfile(fhandle):
    with open(fhandle, 'r') as f1:
        raw = f1.read()
        try:
            gameids = [int(gameid) for gameid in raw.split('\n')]
        except ValueError:
            '''Not all ids in file are valid...'''
            print('Some game ids are not valid; removing invalid ids')
            gameids = list()
            for gameid in raw.split('\n'):
                try: gameids.append(int(gameid))
                except ValueError: pass
        return gameids


def getidswebs(date, cat='NBA'):
    """
    Code for parsing main scores page, given a date and category
    """
    key_phrase = re.compile(r'''var thisGame = new gameObj\("(\d{7,12})".*\)''')
    if verifydate(date):
        date_formatted = date[4:6] + ' ' + date[6:] + ', ' + date[:4]
        print "Attempting to get %s page from %s" % (cat, date_formatted)
        try:
            raw_day_summary = urllib2.urlopen(root_dict[cat]+date).read()
            gameids = key_phrase.findall(raw_day_summary)
            return gameids
        except KeyError:
            print 'Non-valid category, %s, provided; using "NBA"' % cat
            try:
                raw_day_summary = urllib2.urlopen(root_dict['NBA']+date).read()
                gameids = key_phrase.findall(raw_day_summary)
                return gameids
            except urllib2.URLError:
                print 'Failed to fetch ' + root_dict['NBA']+date
        except urllib2.URLError:
            print 'Failed to fetch ' + root_dict[cat]+date


def verifydate(date):
    """
    Checks to make sure provided date is valid format, in past or now.
    Format expected is YYYYMMDD
    """
    now = datetime.datetime.now()
    now = int(str(now.year)+\
               ('0' if now.month<10 else '') + \
               str(now.month)+\
               ('0' if now.day<10 else '') + \
               str(now.day))
    if len(date) != 8:
        print 'WARNING: non-valid date or date in invalid format'
    try:
        if int(date) <= now:
            return True
        else:
            print "WARNING: future date provided; this isn't a crystal ball!!"
            return False
    except ValueError:
        print('non-valid date or date in invalid format: %d' % date)
