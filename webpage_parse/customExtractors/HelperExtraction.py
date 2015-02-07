import sys
import os
import re
import urllib2

from nlppipeline.webpage_parse import (soupypages,
                                       soupypages_helper)
sys.path.append('/Users/immersinn/Gits/')
from dbinterface_python.dbconns import connectMon


meta_dict = {'GizMag': ['keywords','description'],
             'TR': [None]}

'''Calls on soupypages to make soup out of url'''
def getSoup(url,hdr=False):
    out = soupypages.soupFromUrl(url,hdr)
    if out['pass']:
        soup = out['soup']
    else:
        soup = None
    return soup


'''Gets the inline text links'''
def getInlinLinks(ppp,count):
    lnks = dict()
    aas = ppp.find_all(soupypages_helper.a_with_href_wo_at_w_txt)
    for a in aas:
        lnks[count] = (a.text, a['href'])
        count += 1
    return {'links':lnks,'c':count}

'''Replaces the inline links with only the hyperlink text'''
def replaceInlinLinks(content):
    new_content = u''
    InLineLinks = dict()
    ill = list()
    count = 0
    for c in content:
        temp = getInlinLinks(c,count)
        InLineLinks.update(temp['links'])
        new = temp['c']-count
        count = temp['c']
        c = unicode(c)
        for i in range(0,new):
            c = c.replace(' href="'\
                          +InLineLinks[count-1-i][1]+\
                          '" target="_blank">','>')
        new_content += c
    #place all inline into list...
    ill = [{'keyword':InLineLinks[c][0],'link':InLineLinks[c][1]}\
           for c in range(0,len(InLineLinks))]
    return {'c':new_content,'l':ill}

'''Extract all stuff with a 'name' or 'property' feature'''
def getMeta(meta):
    meta_info = dict()
    for m in meta:
        if 'name' in m.attrs.keys():
            meta_info[m.attrs['name']] = m.attrs['content']
        elif 'property' in m.attrs.keys():
            meta_info[m.attrs['property']] = m.attrs['content']
    return meta_info
