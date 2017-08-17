# Author: Chiu-Wang Tseng, 2017.8, BIME NTU
# Web Spider for PTT

import requests as rs
from bs4 import BeautifulSoup as bs
import lxml
import time

class PTTSpider(object):
    def __init__(self, url):
        #url = 'http://www.ptt.cc/bbs/BlackDesert/index.html'
        
        if url[:5] == 'https':
            url = 'http' + url[5:]
        self.url = url
        print('Resolving the url...')
        res = rs.get(url)
        self.soup = bs(res.text, 'lxml')
        print('Done')
        
    def _max_index(self, soup):
        s = soup.select('a')
        for a in s:
            if a.text == '‹ 上頁':
                url_len_diff = len('http://www.ptt.cc'+a.attrs['href']) - len(self.url)
                max_index = int(a.attrs['href'][-5-url_len_diff:-5])+1
                print('Max index:', max_index)
        return max_index

    def _extract_urls(self, max_index, target_index):
        urls = list()
        for i in range(max_index-target_index, max_index, 1):
            _url = self.url[:-5]+str(i+1)+'.html'
            urls.append(_url)
        return urls
    
    def extract_content_pages(self, time_delay=1, proportion=1):
        # time_delay: prevent the server aborting
        max_index = self._max_index(self.soup)
        if proportion>1 or proportion<0:
            pass
        else:
            target_index = int(max_index*proportion)
            print('Target index:', target_index)
        urls = self._extract_urls(max_index, target_index)
        pages = list()
        print('Extracting all the pages from the urls...')
        i = 0
        try:
            for _url in urls:
                time.sleep(time_delay) # prevent aborting
                i += 1
                if i%10 == 0:
                    print('url', i, '...')
                res = rs.get(_url)
                soup = bs(res.text, 'lxml')
                s = soup.select('a')
                for a in s:
                    for k in a.attrs.keys():
                        if k == 'href':
                            if a.attrs['href'][0:len(url)-26] == self.url[-(len(self.url)-17):-10]+'M':
                                url_ = 'http://www.ptt.cc'+a.attrs['href']
                                pages.append(url_)
            print('Done.')
        except:
            pass
            print('Aborting by the server')
        return pages
    
    def _extract_content(self, pages):
        # pages: url array
        htmls = list()
        i = 0
        print('Extracting all contents from the pages...')
        for page in pages:
            i += 1
            if i%10 == 0:
                print('page', i)
            res = rs.get(page)
            htmls.append(res)
        print('Done')
        return htmls
    
    def extract_soup(self, pages):
        htmls = self._extract_content(pages)
        soups = list()
        for html in htmls:
            soup = bs(html.text, 'lxml')
            soups.append(soup)
        return soups
    
    def resolve_soup(self, soups):
        articles = list()
        titles = list()
        contents = list()
        push_contents = list()
        grades = list()
        push_userids = list()
        for soup in soups:
            article = dict()
            title = soup.select('title')
            title = title[0].text
            article['titles'] = title
            titles.append(title)
            meta = soup.select('meta')
            for content in meta:
                for key, val in content.attrs.items():
                    if key == 'name' and val == 'description':
                        article['contents'] = content.attrs['content']
                        contents.append(content.attrs['content'])
            push = dict()
            push['tag'] = list()
            push['userid'] = list()
            push['content'] = list()
            push_content = list()
            push_userid = list()
            span = soup.select('span')
            grade = 0
            for s in span:
                for key, vals in s.attrs.items():
                    for val in vals:
                        if val == 'push-tag':
                            push['tag'].append(s.text)
                            if s.text == '推 ':
                                grade += 1
                            elif s.text == '→ ':
                                pass
                            elif s.text == '噓 ':
                                grade -= 1
                        elif val == 'push-userid':
                            push['userid'].append(s.text)
                            push_userid.append(s.text)
                        elif val == 'push-content':
                            push['content'].append(s.text[2:])
                            push_content.append(s.text[2:])
            push_userids.append(push_userid)
            push['grade'] = grade
            grades.append(grade)
            article['pushes'] = push
            push_contents.append(push_content)
            articles.append(article)
        return articles, [titles, contents, push_contents, push_userids, grades]