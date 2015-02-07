# -*- coding: utf-8 -*-

import sys
from time import sleep

from HelperExtraction import *

tr_main = "http://www.technologyreview.com"

def TRRunme(start,stop):
    '''
    Iterates over pages in [start,stop], grabs all Tech Rev content,
    etc., returns it (or dumps to mongo, really...
    '''
    mdb_conn = connectMon.MongoConn({'db_name':'WebPages',
                                     'coll_name':'TechRev'})
    for p_ind in range(start,stop+1):
        links = TRMainPage(p_ind)
        stories_list = list()
        for ent in links.keys():
            if links[ent].find('graphiti') > -1:
                print(links[ent])
                print('Not an article; skipping document')
            elif links[ent].find('photoessay') > -1:
                print(links[ent])
                print('Not an article; skipping document')
            else:
                try:
                    temp = dict()
                    temp['title'] = ent
                    temp.update(TRStoryPage(links[ent]))
                    if len(temp)>2:
                        stories_list.append(temp)
                except AttributeError:
                    pass
        mdb_conn.MongoInsert(stories_list)
        sleep(3)
        
def TRMainPage(page_num):
    '''Getting the stories from each page'''
    ##/stream/page/2/?sort=recent
    tail = '/stream/page/'
    url = tr_main+tail+str(page_num)+'/'
    print(url)
    soup = getSoup(url,hdr=True)
    if soup:
        body = soup.body if soup.body else soup
        stories = body.find('div','stream-container').\
                  find_all('article')
        links = dict()
        for s in stories:
            c = s.find_all('h1')[0]
            links[c.text] = c.find('a')['href']
        return(links)
    else:
        errmsg = 'No page found at specified url'
        raise RuntimeError, errmsg

def TRStoryPage(url_story):
    '''Getting the content from each story page'''
    ##Grab the individual compontents of the story page:
    url = tr_main+url_story
    print("grabbing story: " + url)
    soup = getSoup(url)
    if soup:
        head = soup.head
        meta = getMeta(head.find_all('meta'))
        body = soup.body if soup.body else soup
        
        ##Operations on the content:
        try:
            content = body.find('article', id='main-article').\
                      find('section','body').\
                      find_all('p')
            ##Grab the inline links, "mark" where they came from, replace with text
            content = replaceInlinLinks(content)
            inline_links = content['l']
            content = content['c']
            article_type = 'Text'
        except AttributeError:
            content = ''
            inline_links = []
            article_type = 'Non-text'

        ##Extra meta stuff:
        if 'parsely-page' in meta.keys():
            meta['parsely-page'] = eval(meta['parsely-page'])
            if 'tags' in meta['parsely-page'].keys():
                meta['keywords'] = meta['parsely-page']['tags']
            author = meta['parsely-page']['author'] \
                     if 'author' in meta['parsely-page'].keys() \
                     else ''

        ##Prep output dictionary:
        out = {'content':content,
               'inline_links':inline_links,
               'meta':meta,
               'author':author,
               'article_type':article_type,
               'site_source':'TechRev'}
    else:
        out = {}
    return(out)

if __name__=="__main__":
    TRRunme(260,1000)



