'''
This handles the grabbing of web-pages using urllib2, and
the making of BeautifulSoup elements from said pages using
Beautiful Soup.  Calls can be made to each separate step,
of or the overall process.  Should likely roll RSS feed
parsing into this as well...
'''



import sys, os
import re
import urllib2
import socket
import ssl
import bs4
from bs4 import BeautifulSoup as bs

'''
General method for grabbing a page at a specified url with
urllib2.  Returns a dictionary:
'pass' (boolean) indicates whether *a* page was grabbed
        w/o any errors
'page' (str) is the page retrieved by the call to the provided
        url.  If an error is encountered, an empty string is ret.
'page_url' (str) is the actual url from which the page ('page')
            was retreived.  In the case of a redirect, this
            differs from the original url.
'''
def makePage(url, hdr=False, timeout=10):
    if hdr:
        hdr = {'User-Agent': 'Mozilla/5.0'}
        url = req = urllib2.Request(url,headers=hdr)
    try:
        conn = urllib2.urlopen(url, timeout=timeout)
        if conn.geturl()==url:
            page_url = url
        else:
            page_url = conn.geturl()
        page = conn.read()
        page = replace_unicode(page)
        return {'page':page, 'pass':True, 'page_url':page_url}
    except urllib2.URLError as X:
        return {'page':'','pass':False,'err':X.__class__}
    except urllib2.httplib.HTTPException as X:
        return {'page':'','pass':False,'err':X.__class__}
    except socket.timeout:
        return {'page':'','pass':False,'err':'timeout'}
    except socket.error:
        return {'page':'','pass':False,'err':'socketerror'}
    except ssl.SSLError:
        return {'page':'','pass':False,'err':'stupidness'}
    except ValueError:
        return {'page':'','pass':False,'err':'unknown url type'}
    


def replace_unicode(uni_str):
    """
    Turn unicode into UTF-8, as that is the format that the
    str class handles, and is the default NLTK character type.
    """
    if type(uni_str)!=str:
        utf8_str = uni_str.encode('utf-8')
    else:
        utf8_str = uni_str
    return utf8_str

##'''
##Remove non-unicode charaters from retreived web pages.
##Need to beef this up...
##'''
##def page_to_unicode(page):
##    page = unicode(re.subn(r'\x92',
##                            "'",
##                            page))
##    page = unicode(replace_unicode(page))
##    return page


'''
does soup have an err key??
parsers:
    html5lib
    lxml
Overrides default / passed parser if 'xmlns' found near
top of page, as this indicates xml encoding, and the lxml
parser typically is superior in these cases.
'''
def makeSoup(page, parser='html5lib'):
    if page:
        if str(page)[:250].find('xmlns=')>-1:
            soup = bs(page, 'lxml')
        else:
            soup = bs(page, parser)
            if not soup.find_all('a'):
                soup = bs(page, 'lxml')
        return {'soup':soup,
                'pass':True}
    else:
        return {'soup':None,
                'pass':False,
                'err':'No page object'}

'''
Does both makePage and makeSoup given a url
'''
def soupFromUrl(url, hdr=False, fail=False, parser='html5lib'):
    page = makePage(url,hdr)
    if page['pass']:
        soup = makeSoup(page['page'],parser=parser)
        if fail:
            return {'page':page['page'],
                    'soup':soup,
                    'pass':True,
                    'page_url':page['page_url']}
        else:
            return soup
    else:
        return {'page':page['page'],
                'soup':[],
                'pass':False,
                'err': 'Page fail: ' + str(page['err'])}


def checkBS4Type(obj, Type):
    bs4ElementTypes = [bs4.element.NavigableString,
                       bs4.element.Tag,
                       bs4.BeautifulSoup]
    if Type=='element':
        return type(obj) in bs4ElementTypes
    elif Type=='Soup':
        return type(obj)==bs4.BeautifulSoup
    elif Type=='Tag':
        return type(obj)==bs4.element.Tag
    elif Type=='NavigableString':
        return type(obj)==bs4.element.NavigableString
    else:
        return 'bad type'


    
