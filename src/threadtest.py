# encoding: utf-8

import threading
import datetime
import json
from CDBLPAuthor import CDBLPAuthor

class ThreadClass(threading.Thread):

    def __init__(self, journal, link):
        threading.Thread.__init__(self)
        self.journal = journal
        self.link = link

    def run(self):
        CDBLPAuthor.parallel_get(self.journal, self.link)
        print(self.journal + ' is done.')

journal_list = [
    {'title': '软件学报', 'href': 'http://cdblp.cn/journal/%E8%BD%AF%E4%BB%B6%E5%AD%A6%E6%8A%A5'},
    {'title': '计算机学报', 'href': 'http://cdblp.cn/journal/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%AD%A6%E6%8A%A5'},
    {'title': '计算机研究与发展', 'href': 'http://cdblp.cn/journal/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%A0%94%E7%A9%B6%E4%B8%8E%E5%8F%91%E5%B1%95'},
    {'title': '计算机工程', 'href': 'http://cdblp.cn/journal/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%B7%A5%E7%A8%8B'},
    {'title': '中国图象图形学报', 'href': 'http://cdblp.cn/journal/%E4%B8%AD%E5%9B%BD%E5%9B%BE%E8%B1%A1%E5%9B%BE%E5%BD%A2%E5%AD%A6%E6%8A%A5'},
    {'title': '中文信息学报', 'href': 'http://cdblp.cn/journal/%E4%B8%AD%E6%96%87%E4%BF%A1%E6%81%AF%E5%AD%A6%E6%8A%A5'},
    {'title': '计算机科学', 'href': 'http://cdblp.cn/journal/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%A7%91%E5%AD%A6'},
    {'title': '小型微型计算机系统', 'href': 'http://cdblp.cn/journal/%E5%B0%8F%E5%9E%8B%E5%BE%AE%E5%9E%8B%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%B3%BB%E7%BB%9F'},
    {'title': '计算机科学与探索', 'href': 'http://cdblp.cn/journal/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%A7%91%E5%AD%A6%E4%B8%8E%E6%8E%A2%E7%B4%A2'},
    {'title': '计算机辅助设计与图形学学报', 'href': 'http://cdblp.cn/journal/%E8%AE%A1%E7%AE%97%E6%9C%BA%E8%BE%85%E5%8A%A9%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%9B%BE%E5%BD%A2%E5%AD%A6%E5%AD%A6%E6%8A%A5'},
    {'title': '中国科学E辑', 'href': 'http://cdblp.cn/journal/%E4%B8%AD%E5%9B%BD%E7%A7%91%E5%AD%A6E%E8%BE%91'},
    {'title': '电子学报', 'href': 'http://cdblp.cn/journal/%E7%94%B5%E5%AD%90%E5%AD%A6%E6%8A%A5'},
    {'title': '计算机科学技术学报(JCST)', 'href': 'http://cdblp.cn/journal/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%A7%91%E5%AD%A6%E6%8A%80%E6%9C%AF%E5%AD%A6%E6%8A%A5%28JCST%29'},
    {'title': '计算机工程与科学', 'href': 'http://cdblp.cn/journal/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%B7%A5%E7%A8%8B%E4%B8%8E%E7%A7%91%E5%AD%A6'}
]

#for journal in journal_list:
#    t = ThreadClass(journal['title'], journal['href'])
#    t.start()

journal_dict = {}
for journal in journal_list:
    separate_cache = open('{}-pub-cache.data'.format(journal['title']), 'r')
    journal_dict[journal['title']] = json.loads(separate_cache.read())
    separate_cache.close()

cache = open('cdblp-pub-cache.data', 'w')
cache.write(json.dumps(journal_dict))
cache.close()