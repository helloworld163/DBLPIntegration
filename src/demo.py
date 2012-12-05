# encoding: utf-8

from pinyin import PinYin
from btpyparse import parse_str as parse_bibtex
from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import json

class DBLPQuery:

    def __init__(self):
        pass

    @staticmethod
    def get_publications_by_author():
        """
        1. Get author's publications from C-DBLP and DBLP
        2. Merge
        """
        pass

    @staticmethod
    def get_coauthors_by_author():
        """
        1. Get author's coauthors from C-DBLP (co-a1) and DBLP (co-a2)
        2. Merge (for intersections of co-a1 and co-a2, judge then merge)
        """
        pass

    @staticmethod
    def get_venues_by_author():
        """
        1. Get author's publications from C-DBLP and DBLP (get_publications_by_author)
        2. Get venues involved
        3. Merge
        """
        pass

    @staticmethod
    def get_authors_by_venue_year():
        """
        1. Read parameters ([{venue: 'SIGMOD', year: 2012}, ...])
        2. Parse parameters to proper query form (DBLP venue by CompleteSearch, C-DBLP venue by manually specifying)
        3. Get authors from each venues (by year)
        4. Merge authors
        """
        pass

    @staticmethod
    def get_coauthored_publications_by_authors():
        """
        1. Get authors' publications
        2. Merge publications
        """
        pass

    @staticmethod
    def get_sample_users():
        cache = open('author-cache.data', 'w')
        piy = PinYin()
        piy.load_word()
        author_list = []
        res = urlopen('http://easyscholar.ruc.edu.cn/moreuser.html')
        dom = BeautifulSoup(res)
        author_tags = dom.find_all(href=re.compile('^homepage/'))
        for author_tag in author_tags:
            if author_tag.findChild('strong'):
                #print(author_tag.findChild('strong').contents)
                author_name = CDBLPAuthor.getEnglishName(author_tag.findChild('strong').contents[0])
                author_list.append(author_name)
                #print('{} {}'.format(author_name['full_name'], author_name['zh']))
                #print(CDBLPAuthor.getEnglishName(author_tag.findChild('strong').contents[0])['full_name'])
                #print(piy.hanzi2pinyin(author_tag.findChild('strong').contents[0]))

        cache.write(json.dumps(author_list))
        cache.close()
        return author_list

    @staticmethod
    def get_cached_authors():
        cache = open('author-cache.data', 'r')
        author_list = json.loads(cache.read())
        cache.close()
        return author_list


class DBLPAuthor:
    def __init__(self, author_urlpt):
        self.author_urlpt = author_urlpt
        #self.author_name = author_name
        self.coauthors = []
        self.publications = []

    def get_coauthors(self):
        response = urlopen('http://dblp.dagstuhl.de/pers/xc/{}'.format(self.author_urlpt))
        soup = BeautifulSoup(response.read())
        coauthor_tags = soup.find_all('author')
        return list(map(lambda a: a.contents[0], coauthor_tags))

    @staticmethod
    def get_authors(author_name):
        author_list_page = urlopen('http://dblp.dagstuhl.de/search/author?xauthor={}'.format(quote(author_name)))
        soup = BeautifulSoup(author_list_page.read())
        author_tags = soup.find_all('author')
        author_urlpts = list(map(lambda a: a['urlpt'], author_tags))
        return author_urlpts


class CDBLPAuthor:
    def __init__(self, author_name):

        # load Chinese-to-PinYin
        self.pinyin = PinYin()
        self.pinyin.load_word()

        self.author_name = author_name
        author_name_en_split = self.pinyin.hanzi2pinyin(self.author_name)
        self.author_name_en = {
            'last_name': author_name_en_split[0].capitalize(),
            'first_name': author_name_en_split[1].capitalize() + ''.join(author_name_en_split[2:])
        }
        self.coauthors = []
        self.coauthors_en = []
        self.publications = []

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


    def getPage(self):
        response = urlopen('http://cdblp.cn/search_result.php?author_name={}'.format(quote(self.author_name)))
        soup = BeautifulSoup(response.read())
        for paper_link in soup.find_all(href=re.compile('^/paper')):
            link = paper_link['href']
            id = re.findall('(\d+\.html$)', link)[0]
            #print(m.groups())
            #print(id)
            
            res = urlopen("http://cdblp.cn/bibtex/{}".format(id))
            s   = BeautifulSoup(res.read())
            bibtex = ''.join(s.find(id='content').find_next_sibling('div').stripped_strings)[6:]
            result = parse_bibtex(bibtex)
            print(result)

    def get_coauthors(self):
        response = urlopen('http://cdblp.cn/search_result.php?author_name={}'.format(quote(self.author_name)))
        soup = BeautifulSoup(response.read())
        coauthor_table = soup.find(id='projectHistory').find_next_sibling('table')
        coauthor_tags = coauthor_table.find_all(href=re.compile('^/author'))
        for coauthor_tag in coauthor_tags:
            author_name_zh = coauthor_tag['href'][8:]
            self.coauthors.append(author_name_zh)
            author_name_en = self.pinyin.hanzi2pinyin(author_name_zh)
            self.coauthors_en.append(
                {
                    'last_name': author_name_en[0].capitalize(),
                    'first_name': author_name_en[1].capitalize() + ''.join(author_name_en[2:])
                }
            )

        #print(self.coauthors)
        return list(map(lambda a: '{} {}'.format(a['first_name'], a['last_name']), self.coauthors_en))

    def q(self):
        pass
        
#test = PinYin()
#test.load_word()
#print(test.hanzi2pinyin('郑庆华'))
#
#author = CDBLPAuthor("郑庆华")
#l1 = author.get_coauthors()
#
#author_q = DBLPAuthor('z/Zheng:Qinghua', '郑庆华')
#l2 = author_q.get_coauthors()
#
#print(set(l1).intersection(set(l2)))

#author_name = '李丽'
#author_CDBLP = CDBLPAuthor(author_name)
#search_name = '{0} {1}'.format(author_CDBLP.author_name_en['first_name'], author_CDBLP.author_name_en['last_name'])
##print(search_name)
##print(DBLPAuthor.get_authors('{0} {1}'.format(author_CDBLP.author_name_en['first_name'], author_CDBLP.author_name_en['last_name'])))
#author_DBLP = [DBLPAuthor(author_urlpt) for author_urlpt in DBLPAuthor.get_authors(search_name)]
#l2 = author_CDBLP.get_coauthors()
#
#for a in author_DBLP:
#    l1 = a.get_coauthors()
#    print('Coauthors of {0} and {1}:'.format(author_name, a.author_urlpt))
#    print(set(l1).intersection(set(l2)))

print(DBLPQuery.get_cached_authors())