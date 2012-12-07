# encoding: utf-8

import threading
from pinyin import PinYin
from urllib.parse import unquote
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString
import re
from DBLPAuthor import DBLPAuthor
from CDBLPAuthor import CDBLPAuthor
from demo import DBLPQuery

class Data():
    result = {}
    objects = {}
    overlaps = {}

    @staticmethod
    def clear():
        Data.result = {}
        Data.objects = {}
        Data.overlaps = {}

class ThreadMatch(threading.Thread):

    def __init__(self, dblp_urlpt, cdblp_author):
        threading.Thread.__init__(self)
        self.dblp_urlpt = dblp_urlpt
        self.cdblp_author = cdblp_author

    def run(self):
        print(self.dblp_urlpt, 'is created.')
        Data.result[self.dblp_urlpt] = DBLPQuery.author_match(self.dblp_urlpt, self.cdblp_author)['ratio']
        Data.objects[self.dblp_urlpt] = DBLPQuery.author_match(self.dblp_urlpt, self.cdblp_author)['object']
        Data.overlaps[self.dblp_urlpt] = DBLPQuery.author_match(self.dblp_urlpt, self.cdblp_author)['overlap']
        print(self.dblp_urlpt, 'is done.')


def get_match(author_name):

    Data.clear()

    author_cdblp = CDBLPAuthor(author_name)
    author_name_comp = CDBLPAuthor.getEnglishName(author_name)

    urlpt = '{}/{}:{}'.format(author_name_comp['last_name'][0].lower(), author_name_comp['last_name'], author_name_comp['first_name'])

    candidate_urlpts = set()
    author_affiliation = dict()

    res = urlopen(DBLPQuery.get_dblp_url(urlpt))
    dom = BeautifulSoup(res)

    for cu_tag in dom.find_all('li', 'homonym'):
        cu = cu_tag.find('a')['href'][3:-5]
        candidate_urlpts.add(cu)
        author_affiliation[cu] = cu_tag.find('a').next_sibling.string

    if len(candidate_urlpts) == 0:
        candidate_urlpts.add(urlpt)
        author_affiliation[urlpt] = 'Default University'

    l = []

    for cu in candidate_urlpts:
        t = ThreadMatch(cu, author_cdblp)
        t.start()
        l.append(t)

    for t in l:
        t.join()

    result = []

    for k, v in Data.result.items():
        if v > 0.1:
            result.append({ 'urlpt': k, 'aff': author_affiliation[k], 'rank': v })

    result.sort(key=lambda i: i['rank'], reverse=True)
    return { 'author': author_cdblp, 'result': result }

def get_publications(author_name):
    #author_name = '王伟'
    result = []
    l = get_match(author_name)
    dom = l['author'].dom
    cdblp_coauthors = l['author'].get_coauthors()
    for candidate in l['result']:

        print(candidate['urlpt'], candidate['aff'])

        dblp_pubs = Data.objects[candidate['urlpt']].get_author()['publications']
        cdblp_pubs = []

        ids = set()
        for ca in cdblp_coauthors:
            if ca['full_name'] in Data.overlaps[candidate['urlpt']]:
                for pub_id in ca['pubs']:
                    if not pub_id in ids:
                        ids.add(pub_id)
                        #print(pub_id)
                        paper_link_tag = dom.find('a', attrs={'name': pub_id})
                        # table cell tag
                        try:
                            td_tag = paper_link_tag.parent
                        except AttributeError:
                            print(pub_id)
                            continue
                        # title
                        title = paper_link_tag.string
                        link = paper_link_tag['href']
                        cdblbkey = re.findall('(\d+)(\.html$)', link)[0][0]
                        # authors
                        authors = []
                        counter = 0
                        for author_tag in td_tag.find_all(href=re.compile('^/author')):
                            if counter == 0:
                                current_author = author_tag.previous_sibling
                                if type(current_author) == NavigableString and author_name in current_author.string:
                                    authors.append(current_author.string.strip())

                            if isinstance(author_tag.string, str):
                                authors.append(author_tag.string.strip())

                            current_author = author_tag.next_sibling
                            if type(current_author) == NavigableString and author_name in current_author.string:
                                authors.append(current_author.string.replace('.', '').strip())

                            counter += 1

                        # publication data
                        venue_rec = td_tag.find_all(href=re.compile('^/journal'))
                        venue = venue_rec[0].string
                        volume_result = re.compile('(/journal)/(.*)/(\d*)/(.*)').findall(venue_rec[1]['href'])[0]
                        issue_result = re.compile('(/journal_issue)/(.*)/(\d*)/(.*)').findall(venue_rec[2]['href'])[0]
                        year = volume_result[-2]
                        volume = volume_result[-1]
                        number = issue_result[-1]
                        pages = venue_rec[-1].next_sibling.string.replace(':', '').strip()

                        publication = {
                            'title': title,
                            'authors': authors,
                            'venue-type': 'journal',
                            'venue': venue,
                            'volume': unquote(volume),
                            'number': unquote(number),
                            'pages': pages,
                            'year': year,
                            'cdblpkey': cdblbkey
                        }

                        cdblp_pubs.append(publication)

        result.append({'urlpt': candidate['urlpt'], 'aff': candidate['aff'], 'cdblp': cdblp_pubs, 'dblp': dblp_pubs})

    return result

def get_publications_by_u(cached_list, cached_set, author_name):
    trial = author_name[0]

    if author_name in cached_set:
        #d = DBLPQuery.get_cache('author-entries-cache.data')
        print('This is a CDBLP author w/ a English name on file.')
        author_name_zh = ''
        for author_name_comp in cached_list:
            if author_name_comp['full_name'] == author_name.strip() or author_name_comp['zh'] == author_name:
                author_name_zh = author_name_comp['zh']
                break

        return get_publications(author_name_zh)

    elif 0x3400 < ord(trial) < 0x2b6f8:

        print('This is a CDBLP author w/ a Chinese name.')
        return get_publications(author_name)

    else:

        print('This is a non-CDBLP author.')
        candidates = []
        res = urlopen('{}/search/author?xauthor={}'.format(DBLPQuery.base_url, quote(author_name)))
        dom = BeautifulSoup(res)
        for candidate_tag in dom.find_all('author'):
            if author_name == candidate_tag.string:
                candidates.append(DBLPAuthor(candidate_tag['urlpt']))

        return [{ 'urlpt': candidates[0].author_urlpt, 'aff': 'None', 'cdblp': {}, 'dblp': candidates[0].get_author()['publications'] }]