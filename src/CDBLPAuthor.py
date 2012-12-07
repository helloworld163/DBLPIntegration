# encoding: utf-8

from pinyin import PinYin
from btpyparse import parse_str as parse_bibtex
from urllib.request import urlopen
from urllib.parse import quote, unquote
import urllib.error
from bs4.element import NavigableString
from bs4 import BeautifulSoup
import re
import json

class CDBLPAuthor:

    pinyin = PinYin()
    pinyin.load_word()

    def __init__(self, author_name, link=''):

        self.author_name = CDBLPAuthor.getEnglishName(author_name)

        if not link:
            link = 'http://cdblp.cn/search_result.php?author_name={}&area=computer'.format(quote(self.author_name['zh']))

        self.res = urlopen(link)
        self.dom = BeautifulSoup(self.res)

        #self.get_all_authors()

        self.author = {
            'author_name': {},
            'coauthors': [],
            'publications': [
                {
                    'title': 'Ranking the Difficulty Level of the Knowledge Units Based on Learning Dependency',
                    'authors': ['Jun Liu', 'Sha Sha', 'Qinghua Zheng', 'Wei Zhang'],
                    'venue-type': 'journal',
                    'venue': 'IJDET',
                    'volume': '',
                    'number': '',
                    'pages': '',
                    'year': '2012',
                    'cdblpkey': '83594'
                }
            ]
        }

    def get_all_authors(self):

        l = []

        all_name_tags = self.dom.find_all(href=re.compile('namedisambiguation'))

        i = 0
        for name_tag in all_name_tags:
            if name_tag.string != 'Unknown':
                print(i, self.author_name['zh'], 'from', name_tag.string)
                l.append('http://cdblp.cn' + name_tag['href'][5:])
            i += 1

        c = int(input('There are several authors under this name, which one do you want to choose?\n> '))
        if c < 0:
            c = 0

        self.res = urlopen(l[c])
        self.dom = BeautifulSoup(self.res)

        return l[c]

    def get_author(self):

        coauthors = self.get_coauthors()
        publications = []

        paper_link_tags = self.dom.find_all(href=re.compile('^/paper'))

        for paper_link_tag in paper_link_tags:
            # table cell tag
            td_tag = paper_link_tag.parent
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
                    if type(current_author) == NavigableString and self.author_name['zh'] in current_author.string:
                        authors.append(current_author.string.strip())

                if isinstance(author_tag.string, str):
                    authors.append(author_tag.string.strip())

                current_author = author_tag.next_sibling
                if type(current_author) == NavigableString and self.author_name['zh'] in current_author.string:
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

            publications.append(publication)

        self.author = {
            'author_name': self.author_name,
            'coauthors': coauthors,
            'publications': publications
        }

        return self.author



    def get_coauthors(self):
        coauthors = []

        coauthor_table = self.dom.find_all('table')[-2]
        coauthor_tags = coauthor_table.find_all(href=re.compile('^/author'))
        for coauthor_tag in coauthor_tags:
            coauthored_pub_tags = coauthor_tag.parent.find_next_sibling('td').find_all('a')
            author = CDBLPAuthor.getEnglishName(coauthor_tag.string.strip())
            author['count'] = len(coauthored_pub_tags)
            author['pubs'] = map(lambda t: t['href'][1:], coauthored_pub_tags)
            coauthors.append(author)

        return coauthors
        #return list(map(lambda a: '{} {}'.format(a['first_name'], a['last_name']), self.coauthors_en))

    @staticmethod
    def getEnglishName(author_name_zh):

        author_name_en_split = CDBLPAuthor.pinyin.hanzi2pinyin(author_name_zh.strip())
        # return author's English name
        if isinstance(author_name_en_split, str):
            author_name = {
                'full_name': author_name_en_split
            }

        else:
            if len(author_name_zh) > 1:
                author_name = {
                    'zh': author_name_zh,
                    'last_name': author_name_en_split[0].capitalize(),
                    'first_name': author_name_en_split[1].capitalize() + ''.join(author_name_en_split[2:])
                }
                author_name['full_name'] = '{} {}'.format(author_name['first_name'], author_name['last_name'])
                author_name['full_name_reverse'] = '{} {}'.format(author_name['last_name'], author_name['first_name'])
                if len(author_name_zh) == 3:
                    author_name['full_name_dash'] = '{}-{} {}'.format(author_name_en_split[1].capitalize(), author_name_en_split[2], author_name['last_name'])
            else:
                author_name = {
                    'zh': author_name_zh,
                    'last_name': author_name_en_split[0].capitalize(),
                    'first_name': ''
                }
                author_name['full_name'] = '{} {}'.format(author_name['first_name'], author_name['last_name'])
                author_name['full_name_reverse'] = '{} {}'.format(author_name['last_name'], author_name['first_name'])


        return author_name

    @staticmethod
    def get_english_name(author_name_zh, py_obj):

        author_name_en_split = py_obj.hanzi2pinyin(author_name_zh.strip())
        # return author's English name
        if isinstance(author_name_en_split, str):
            author_name = {
                'full_name': author_name_en_split
            }

        else:
            if len(author_name_zh) > 1:
                author_name = {
                    'zh': author_name_zh,
                    'last_name': author_name_en_split[0].capitalize(),
                    'first_name': author_name_en_split[1].capitalize() + ''.join(author_name_en_split[2:])
                }
                author_name['full_name'] = '{} {}'.format(author_name['first_name'], author_name['last_name'])
                author_name['full_name_reverse'] = '{} {}'.format(author_name['last_name'], author_name['first_name'])
                if len(author_name_zh) == 3:
                    author_name['full_name_dash'] = '{}-{} {}'.format(author_name_en_split[1].capitalize(), author_name_en_split[2], author_name['last_name'])
            else:
                author_name = {
                    'zh': author_name_zh,
                    'last_name': author_name_en_split[0].capitalize(),
                    'first_name': ''
                }
                author_name['full_name'] = '{} {}'.format(author_name['first_name'], author_name['last_name'])
                author_name['full_name_reverse'] = '{} {}'.format(author_name['last_name'], author_name['first_name'])


        return author_name

    @staticmethod
    def get_publications_by_journal(journal, year, issue):
        res = urlopen('http://cdblp.cn/journal_issue/' + quote('{}/{}/{}'.format(journal, year, issue)))
        dom = BeautifulSoup(res)
        publications = []

        paper_link_tags = dom.find_all(href=re.compile('^/paper'))
        for paper_link_tag in paper_link_tags:
            # table cell tag
            td_tag = paper_link_tag.parent
            # title
            title = paper_link_tag.string
            link = paper_link_tag['href']
            cdblbkey = re.findall('(\d+)(\.html$)', link)[0][0]
            # authors
            authors = []
            for author_tag in td_tag.find_all(href=re.compile('^/author')):
                author_name = author_tag.contents[0]
                if isinstance(author_name, str):
                    authors.append(author_name.strip())

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

            publications.append(publication)

        return publications

    @staticmethod
    def get_publication_dict():

        publication_dict = {}

        res = urlopen('http://cdblp.cn/jour_scan.php?fid=journalscan')
        category_dom = BeautifulSoup(res)

        print(list(map(lambda c: { 'title': c.string, 'href': 'http://cdblp.cn' + c['href'] }, category_dom.find_all(href=re.compile('^/journal')))))

        for journal_tag in category_dom.find_all(href=re.compile('^/journal')):

            journal = journal_tag.string
            print(journal)
            print('http://cdblp.cn' + journal_tag['href'])
            publication_dict[journal] = {}

            res = urlopen('http://cdblp.cn' + journal_tag['href'])
            journal_dom = BeautifulSoup(res)

            for issue_tag in journal_dom.find_all(href=re.compile('^/journal_issue')):
                print(issue_tag.string)
                print(issue_tag['href'])

                issue_result = re.compile('(/journal_issue)/(.*)/(\d*)/(.*)').findall(issue_tag['href'])[0]
                year = issue_result[-2]
                issue = unquote(issue_result[-1])
                publications = CDBLPAuthor.get_publications_by_journal(journal, year, issue)

                if not publication_dict[journal].__contains__(year):
                    publication_dict[journal][year] = {}

                publication_dict[journal][year][issue] = publications

        return publication_dict

    @staticmethod
    def parallel_get(journal, link):

        publication_dict = {}

        print(journal)
        print(link)

        res = urlopen(link)
        journal_dom = BeautifulSoup(res)

        for issue_tag in journal_dom.find_all(href=re.compile('^/journal_issue')):
            #print(issue_tag.string)
            #print(issue_tag['href'])
            try:
                issue_result = re.compile('(/journal_issue)/(.*)/(\d*)/(.*)').findall(issue_tag['href'])[0]
                year = issue_result[-2]
                issue = unquote(issue_result[-1])
                publications = CDBLPAuthor.get_publications_by_journal(journal, year, issue)

                if not publication_dict.__contains__(year):
                    publication_dict[year] = {}

                publication_dict[year][issue] = publications
            except AttributeError as e:
                print(journal + year + issue)
                print(e)
            except TypeError as et:
                print(journal + year + issue)
                print(et)
            except urllib.error.HTTPError as eh:
                print(journal + year + issue)
                print(eh)

        cache = open('{}-pub-cache.data'.format(journal), 'w')
        cache.write(json.dumps(publication_dict))
        cache.close()

        return publication_dict

if __name__ == '__main__':
    z = CDBLPAuthor('王伟')
    print(z.get_all_authors())
    #print(z.get_author())
    pass