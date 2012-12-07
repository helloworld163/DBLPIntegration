from pinyin import PinYin
from btpyparse import parse_str as parse_bibtex
from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import json

class DBLPAuthor:

    base_url = 'http://dblp.dagstuhl.de'

    def __init__(self, author_urlpt):
        self.author_urlpt = author_urlpt
        self.author_name = ''
        self.coauthor_res = urlopen('{}/pers/xc/{}'.format(DBLPAuthor.base_url, self.author_urlpt))
        self.coauthor_dom = BeautifulSoup(self.coauthor_res)
        self.page_res = urlopen('{}/pers/hc/{}'.format(DBLPAuthor.base_url, self.author_urlpt))
        self.page_dom = BeautifulSoup(self.page_res)
        #self.author_name = author_name
        self.coauthors = []
        self.publications = []
        self.author = {
            'author_name': '',
            'coauthors': [],
            'publications': [
                {
                    'title': 'Ranking the Difficulty Level of the Knowledge Units Based on Learning Dependency',
                    'authors': ['Jun Liu', 'Sha Sha', 'Qinghua Zheng', 'Wei Zhang'],
                    'venue-type': 'journal',
                    'venue': 'IJDET',
                    'year': '2012',
                    'dblp-key': 'journals/ijdet/LiuSZZ12'
                }
            ]
        }

    def get_author(self):

        publications = []
        publication_tags = self.page_dom.find_all('div', 'data')
        for publication_tag in publication_tags:
            authors = []

            # title
            title = publication_tag.findChild('span', 'title').contents[0]

            # authors
            counter = 0
            for author_tag in publication_tag.findChildren(href=re.compile('pers/hd/')):
                # get author's name
                author_name = author_tag.contents[0]
                # get author's urlpt
                regex = re.compile("(pers/hd/)(.*)(\.html$)")
                try:
                    author_urlpt = regex.findall(author_tag['href'])[0][1]
                except:
                    author_urlpt = ''
                    print('Err:', author_tag['href'])
                # add author to list
                if counter == 0:
                    if author_tag.find_previous_sibling('span', 'this-person'):
                        self.author_name = author_tag.find_previous_sibling('span', 'this-person').contents[0]
                        authors.append({
                            'name': self.author_name,
                            'urlpt': self.author_urlpt
                        })

                authors.append({
                    'name': author_name,
                    'urlpt': author_urlpt
                })

                if author_tag.find_next_sibling('span', 'this-person'):
                    self.author_name = author_tag.find_next_sibling('span', 'this-person').contents[0]
                    authors.append({
                        'name': self.author_name,
                        'urlpt': self.author_urlpt
                    })

                counter += 1

            # dblp-key
            dblpkey_tag = publication_tag.findChild(href=re.compile('(/db/)(\w*)/(\w*)/(.*\.html#)(.*)'))
            try:
                result = re.compile('(/db/)(\w*)/(\w*)/(.*)(\.html#)(.*)').findall(dblpkey_tag['href'])[0]
                #print(result)
                venue_type = result[1]
                venue = result[2]
                venue_order = result[3]
                key = result[5]
                misc = dblpkey_tag.next_sibling
                year_2bit = key[-2:]
                year = ''
                if year_2bit > '20':
                    year = '19' + year_2bit
                else:
                    year = '20' + year_2bit
                publication = {
                    'title': title,
                    'authors': authors,
                    'venue-type': venue_type,
                    'venue': venue.upper(),
                    'venue-order': venue_order,
                    'dblpkey': '{}/{}/{}'.format(venue_type, venue, key),
                    'misc': misc,
                    'year': year
                }
                publications.append(publication)
            except TypeError:
                pass

        self.author = {
            'author_name': self.author_name,
            'coauthors': self.get_coauthors(),
            'publications': publications
        }

        return self.author


    def get_coauthors(self):
        coauthor_tags = self.coauthor_dom.find_all('author')
        self.author['coauthors'] = list(map(lambda a: a.contents[0], coauthor_tags))
        return self.author['coauthors']

    def get_coauthors_with_count(self):
        coauthor_tags = self.coauthor_dom.find_all('author')
        coauthors = list(map(lambda a: {'name': a.string, 'urlpt': a['urlpt'], 'count': int(a['count']) }, coauthor_tags))
        return coauthors

    @staticmethod
    def get_authors(author_name):
        res = urlopen('http://dblp.dagstuhl.de/search/author?xauthor={}'.format(quote(author_name)))
        dom = BeautifulSoup(res)
        author_tags = dom.find_all('author')
        author_urlpts = list(map(lambda a: a['urlpt'], author_tags))
        return author_urlpts


if __name__ == '__main__':

    z = DBLPAuthor('w/Wu:Chaohui')
    print(z.get_author())