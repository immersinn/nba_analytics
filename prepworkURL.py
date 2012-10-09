'''
General set of tools for grabbing web pages and extracting relevant info
from them; as of now, 'geared' towards use with ESPN parsing stuff; hope-
fully will expand to other ventures in the near future;
'''

import sys, os
import urllib2
import HTMLParser

from bs4 import BeautifulSoup

def makePage(url):
    '''
    Grabs a file handle for the page at URL; does basic error handling
    '''
    try:
        page = urllib2.urlopen(url).read()
    except urllib2.URLError:
        print '!!Failed to fetch ' + url
        page = ''
        #continue
    except ValueError:
        print "!!unknown url type: %s" % url
        page = ''
        #continue
    return page

def makeSoup(page, url, parser='html5lib'):
    '''
    Makes soup out of "page" file handle (typically a 'live' web-page,
    though could also be a locally-saved HTML file...)
    '''
    try:
        soup = BeautifulSoup(page, parser)
    except HTMLParser.HTMLParseError:
        print '!!Failed to parse ' + url
        soup = None
        #continue
    return soup
