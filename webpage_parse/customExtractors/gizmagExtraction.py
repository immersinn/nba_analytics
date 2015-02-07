# -*- coding: utf-8 -*-

import sys
from time import sleep
import urllib2

#from bs4 import BeautifulSoup as bs

from HelperExtraction import *

giz_main = "http://www.gizmag.com"

def GizRunme(start,stop):
    """
    Iterates over pages in [start,stop], grabs all Giz content,
    etc., returns it (or dumps to mongo, really...
    """
    mdb_conn = connectMon.MongoConn({'db_name':'WebPages',
                                     'coll_name':'GizMag'})
    for p_ind in range(start,stop+1):
        links = GizMainPage(p_ind)
        stories_list = list()
        for ent in links.keys():
            try:
                temp = dict()
                temp['title'] = ent
                temp.update(GizStoryPage(links[ent]))
                if len(temp)>2:
                    stories_list.append(temp)
            except AttributeError:
                pass
        mdb_conn.MongoInsert(stories_list)
        sleep(3)

def GizMainPage(page_num):
    '''Getting the stories from each page'''
    tail = '/page/'
    url = giz_main+tail+str(page_num)+'/'
    print(url)
    soup = getSoup(url,hdr=True)
    if soup:
        body = soup.body if soup.body else soup
        content = body.find_all('div',id='content')
        stories = content[0].find_all('div','summary_item')
        links = dict()
        for s in stories:
            c = s.find_all('h2')[0]
            links[c.text] = c.find('a')['href']
        return(links)
    else:
        errmsg = 'No page found at specified url'
        raise RuntimeError, errmsg

def GizStoryPage(url_story):
    '''Getting the content from each story page'''
    ##Grab the individual compontents of the story page:
    url = giz_main+url_story
    print("grabbing story: " + url)
    soup = getSoup(url)
    if soup:
        head = soup.head
        meta = getMeta(head.find_all('meta'))
        body = soup.body

        ##Operations on the content:
        try:
            content = body.find_all('div','article_body')[0].find_all('p')
            ##See if there's a source...
            source = getSource(content)
            content = source['c']; source = source['s']
            ##Grab related content / other articles at end of current article
            ##All are internal to Gizmag.
            related = getRelLinks(body.find_all('div',id='related_articles')[0])
            ##Grab the inline links, "mark" where they came from, replace with text
            content = replaceInlinLinks(content)
            inline_links = content['l']
            content = content['c']
            article_type = 'Text'
        except AttributeError:
            content = ''
            inline_links = []
            source = ''
            related = []
            article_type = 'Non-text'

        ##Get the author url
        author = body.find('a',rel='author')
        if author:
            author = author['href']
        else:
            author = ''
        if author:
            ##Prep output dictionary:
            out = {'content':content,
                   'inline_links':inline_links,
                   'related_links':related,
                   'story_source':source,
                   'meta':meta,
                   'author':author,
                   'atricle_type':article_type,
                   'site_source':'GizMag'}
        else:
            out = {}
    else:
        out = {}
    return(out)


def getSource(content):
    """
    If there is a source listed at the end of the story,
    this grabs it and denotes it as such
    """
    if content[-1].text.lower().startswith('source'):
        source = (content[-1].find('a').text,content[-1].find('a')['href'])
        #ditch source from content, since we have it coded now
        content = content[:-1]
    else:
        source = ()
    return {'c':content,'s':source}

    
def getRelLinks(related):
    """
    Gets all the related links from the related links portion
    of the story
    """
    rel_links = related.find_all('a')
    rel_list = list()
    for r in rel_links:
        temp = dict()
	if 'title' in r.attrs.keys():
            temp['title'] = r['title']
            temp['link'] = r['href']
        else:
            temp['title'] = r.text
            temp['link'] = r['href']
        rel_list.append(temp)
    return rel_list


if __name__=="__main__":
    GizRunme(1,1000)
    

"""
http://www.gizmag.com/page/354/
grabbing story: http://www.gizmag.com/fotopro-master-kit-iphone/29937/
Traceback (most recent call last):
  File "sand_gizmagExtraction.py", line 145, in <module>
    GizRunme(1,1000)
  File "sand_gizmagExtraction.py", line 29, in GizRunme
    temp.update(GizStoryPage(links[ent]))
  File "sand_gizmagExtraction.py", line 71, in GizStoryPage
    source = getSource(content)
  File "sand_gizmagExtraction.py", line 117, in getSource
    source = (content[-1].find('a').text,content[-1].find('a')['href'])
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/bs4/element.py", line 905, in __getitem__
    return self.attrs[key]
KeyError: 'href'
"""
