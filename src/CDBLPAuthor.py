from pinyin import PinYin
from btpyparse import parse_str as parse_bibtex
from urllib.request import urlopen
from urllib.parse import quote, unquote
from bs4.element import NavigableString
from bs4 import BeautifulSoup
import re
import json

class CDBLPAuthor:
    def __init__(self, author_name):

        self.author_name = CDBLPAuthor.getEnglishName(author_name)

        self.res = urlopen('http://cdblp.cn/search_result.php?author_name={}'.format(quote(self.author_name['zh'])))
        self.dom = BeautifulSoup(self.res)

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

        coauthor_table = self.dom.find(id='projectHistory').find_next_sibling('table')
        coauthor_tags = coauthor_table.find_all(href=re.compile('^/author'))
        for coauthor_tag in coauthor_tags:
            coauthors.append(CDBLPAuthor.getEnglishName(coauthor_tag.string.strip()))

        return coauthors
        #return list(map(lambda a: '{} {}'.format(a['first_name'], a['last_name']), self.coauthors_en))

    @staticmethod
    def getEnglishName(author_name_zh):
        pinyin = PinYin()
        pinyin.load_word()
        author_name_en_split = pinyin.hanzi2pinyin(author_name_zh.strip())
        # return author's English name
        author_name = {
            'zh': author_name_zh,
            'last_name': author_name_en_split[0].capitalize(),
            'first_name': author_name_en_split[1].capitalize() + ''.join(author_name_en_split[2:])
        }
        author_name['full_name'] = '{} {}'.format(author_name['first_name'], author_name['last_name'])
        author_name['full_name_reverse'] = '{} {}'.format(author_name['last_name'], author_name['first_name'])
        return author_name

if __name__ == '__main__':
    z = CDBLPAuthor('刘均')
    print(z.get_author())