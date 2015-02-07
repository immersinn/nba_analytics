'''
General wrapper for soupypages to be used in class objects to add
'page' and 'soup' attributes to the object.  Also handles testing
of output from soupypages to see if actual page / soup returned.
Also contains several helper functions for 'find_all' to filter
results.
'''
import re
import bs4
import soupypages

'''
Makes call to soupypages to obtain page corresponding to url if no
page associated with object yet.  Else, requests user re-call with
over-write==True if they really want to go through with it.
'''
def get_page(obj, overw=False):
    if not 'page' in set(dir(obj)) or\
       not obj.page or\
       overw == True:
        obj = view_page(obj, soupypages.makePage(obj.url,
                                                 hdr=True))
    else:
        print('Page already retreived. To over-write, recall with overw=True')
    return obj


'''
Obtains soup associated with url.  If no page yet, gets page and
converts to soup.  If page but no soup, just gets soup.  If soup and
not over-write, requests user recall with overw==True.  If obj.page
has been set to an empty string (i.e., ''), then this assumes that the
page retreival was a failure, and does not re-attempt, else there is
an inf looping issue.
'''
def get_soup(obj, overw=False):
    if not 'soup' in set(dir(obj)) or\
       overw == True:
        if not 'page' in set(dir(obj)):
            obj = get_page(obj)
            obj = get_soup(obj)
        else:
            obj = taste_soup(obj, soupypages.makeSoup(obj.page))
    else:
        print('Soup already on table. To reorder, call with overw=True')
    return obj


'''
Checks page call to soupypages to see if page successfully
obtained from url.
Also checks if page has "sufficient" content.
If not, looks for redirect links on the page that was grabbed.
If found, switches the URL associated with self to the redirect
link, and continues.
Under if out['pass']:
    1st:  checks if suff content.  If not, looks for redirect on page,
        calls get_page with new link
    2nd:  checks if an anto redirect occured.  If yes, changes link to
        link that was used.
    3rd:  things went as planned, yo.
'''
def view_page(obj, out, verbose=False):
    if out['pass']:
        if len(out['page'])<1000:
            obj = manual_redirect(out, obj, verbose=verbose)
        elif obj.url!=out['page_url']:
            obj.url = out['page_url']
            if verbose: print('Page redirect:  ' + obj.url)
            obj.page = out['page']
        else:
            obj.page = out['page']
        if verbose: print('I see page')
    else:
        obj.page = ''
        print('Error in retreiving page:  %s' % out['err'])
    return obj


def manual_redirect(out, obj, verbose=False):
    s_out = soupypages.makeSoup(out['page'])
    if s_out['pass']:
        soup = s_out['soup']
        meta = soup.find_all('meta')
        if len(meta)>0:
            for m in meta:
                try:
                    if m['http-equiv'].lower()=='refresh':
                        try:
                            if m['content'].lower().find('url')>-1:
                                new_url = prepend_url(obj.url,
                                                      re.split(u'url=',
                                                               m['content'].lower())[1])
                                if new_url != obj.url:
                                    obj.url = new_url
                                    obj = get_page(obj, overw=True)
                                if verbose:
                                    print('Broken auto-redirect; manual redirect performed.')
                        except KeyError:
                            obj.page = out['page']
                            obj.soup = ''
                except KeyError:
                    obj.page = out['page']
                    obj.soup = ''
        else:
            obj.page = out['page']
            obj.soup = ''
    else:
        obj.page = out['page']
        obj.soup = ''
    return obj


def manual_redirect_02():
    '''
    Check for pages with incorrect links that provide re-directs that
    were not followed for some reason by urllib2.
    1000 seems to be an idela cutoff lengthfor page size.  "Dead zone"
    from 1000-3000ish.
    '''
    dept_conn = connectMon.MongoConn({'db_name':'EduCrawl',
                                      'coll_name':'Department'})
    dept_conn.query({"$where":"this.Page.length<1000"})
    ##soupypages.makeSoup(short_pages[0][1].strip(r')|(').split(',')[0])

    for i in range(dept_conn.LastQLen):
        cp = dept_conn.LastQ.next()
        if cp['Page']:
            soup = soupypages.makeSoup(cp['Page'])
            meta = soup['soup'].find_all('meta')
            for m in meta:
                try:
                    if m['http-equiv'].lower()=='refresh':
                        try:
                            if m['content'].lower().find('url'):
                                cp['Link'] = soupypages_helper.prepend_url(cp['Link'],
                                                    re.split(u'url=',
                                                             m['content'].lower())[1])
                                new_page = soupypages.makePage(cp['Link'])
                                if new_page['pass']:
                                    cp['Page'] = new_page['page']
                                    dept_conn.coll.update({"_id":cp["_id"]},cp)
                                    print(cp["_id"])
                                    break
                        except KeyError:
                            pass
                except KeyError:
                    pass


'''
Checks output from soupypages call to see if soup successfully
obtained.
'''
def taste_soup(obj, out, verbose=False):
    if out['pass']:
        obj.soup = out['soup']
        if verbose: print('Yum, soup!!')
    else:
        obj.soup = ''
        print('There\'s a fly in my soup!!')
        print(out['err'])
    return obj

'''
Special function to throw to soup.find_all().  Returns true for
all <a>'s with an href (e.g., hyperlink) attribute and text
attribute matching the reg_ex passed.
'''
def a_with_href_wo_at_w_txt(tag,
                            t_type='a',
                            text=True,
                            reg_ex=None,
                            oth_cond=lambda x: True):
    if not text:
         return tag.name.lower()==t_type and\
               'href' in tag.attrs and\
               not '@' in tag['href'] and\
               not tag['href'].startswith('mailto:')
    elif not reg_ex:
        return tag.name==t_type and\
               'href' in tag.attrs and\
               not '@' in tag['href'] and\
               not tag['href'].startswith('mailto:') and\
               'text' in set(dir(tag)) and\
               tag.text and\
               oth_cond(tag.text)
    else:
        return tag.name==t_type and\
               'href' in tag.attrs and\
               not '@' in tag['href'] and\
               not tag['href'].startswith('mailto:') and\
               'text' in set(dir(tag)) and\
               re.search(reg_ex, tag.text.lower()) and\
               oth_cond(tag.text)


def src_filter(tag):
    return 'src' in tag.__dict__['attrs'].keys()


def clean_src_link(link):
    if not link.startswith('http://'):
        link = link.strip('/')
        link = 'http://' + link
    return link
    

'''
Finds and returns all headers in the soup at the specified
level(s).  Default is all headers through h3's, including
h's
'''
def headers_find(tag, text=True, reg_ex=None, h_reg_ex=r'^h[1-3]?$'):
    if not text:
        return re.search(h_reg_ex, tag.name.lower())
    elif not reg_ex:
        return re.search(h_reg_ex, tag.name.lower()) and\
               'text' in set(dir(tag))
    else:
        return re.search(h_reg_ex, tag.name.lower()) and\
               'text' in set(dir(tag)) and\
               re.search(reg_ex, tag.text.lower())
        
'''
Special function to throw to soup.find_all().  Returns true for
all <div>'s with class equal to ctype.
'''
def div_class_find(tag, ctype=None):
    if not ctype:
        return tag.name=='div' and\
               'class' in tag.attrs
    else:
        return tag.name=='div' and\
               'class' in tag.attrs and\
               tag['class'] == ctype


'''
OK, there has got to be a better way to do this, but here it goes:
First, we get all 'a' html objects.  Then we look for hrefs in each
of these objects.  If a particular link is already present, we merge
the text associated with that link.  We then reverse the dictionary,
(why??) and modify the text value if we've seen it before in the object.
'''
def get_urls(soup_obj, page_url):
    urls = [(k.text.strip(),
             helper.prepend_url(page_url,
                                k['href'],
                                no_tupe=True))\
            for k in soup_obj.find_all(a_with_href_wo_at_w_txt)]
    if not urls:
        if a_with_href_wo_at_w_txt(html_obj):
            urls = [(soup_obj.text.strip(),
                     prepend_url(page_url,
                                 soup_obj['href'],
                                 no_tupe=True))]
    if urls:
        return urls
    else:
        raise AttributeError


'''
On many sites, embedded urls linking to other pages within site
only list partial urls, starting with the alst common directory
between the current page and the page the links points to.  This
pre-pends those partial urls with the appropriate info so that
they may be used in the future by python.
cucs_url.split('/').index(urls.values()[0].strip('/').split('/')[0])
'''
def prepend_urls(source_url, all_urls):
    for i in all_urls.keys():
        urls = all_urls[i]
        for j,(k,u) in enumerate(urls):
            urls[j] = prepend_url(source_url, u)
        all_urls[i] = urls
    return all_urls


## prob need to do something w/ k
def prepend_url(source_url, url, k=None, no_tupe=False):
    url = url.strip().strip("\\'")
    if not url.startswith('http'):
        if url.startswith('.'):
            url = ''.join([source_url,
                           url[2:]])
        else:
            try:
                last_common = source_url.split('/').index(\
                    url.strip('/').split('/')[0])
                url = (k,'/'.join(\
                    ['/'.join(\
                        source_url.split('/')[:last_common]),url.lstrip('/')]))
                if no_tupe:
                    url = url[1]
            except ValueError:
                url = source_url.rstrip('/') + '/' + url.lstrip('/')
    return url
