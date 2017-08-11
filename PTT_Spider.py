# Author: Chiu-Wang Tseng, 2017.8, lab301 BIME NTU
# Web Spider for PTT

import requests as rs
from bs4 import BeautifulSoup as bs
import lxml
import time

class PTTSpider(object):
    def __init__(self, url):
        #url = 'http://www.ptt.cc/bbs/BlackDesert/index.html'
        # main url 
        # normalize the url as http
        if url[:5] == 'https':
            url = 'http' + url[5:]
        self.url = url
        print('Resolving the url...')
        # request the main url 
        res = rs.get(url)
        # resolve the result by bs4
        self.soup = bs(res.text, 'lxml')
        print('Done')
        
    def _max_index(self, soup):
        # return the max index of the pages under the main url
        s = soup.select('a')
        for a in s:
            # find the max index by the href of '‹ 上頁' label
            if a.text == '‹ 上頁':
                url_len_diff = len('http://www.ptt.cc'+a.attrs['href']) - len(self.url)
                max_index = int(a.attrs['href'][-5-url_len_diff:-5])+1
                print('Max index:', max_index)
        return max_index

    def _extract_urls(self, max_index, target_index):
        # extract all the url of the indexes
        urls = list()
        for i in range(max_index-target_index, max_index, 1):
            _url = self.url[:-5]+str(i+1)+'.html'
            urls.append(_url)
        return urls
    
    def extract_content_pages(self, time_delay=1, proportion=1):
        # extract all the content url from all the url of the indexes
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
                # resolving the url
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
        # extract all the contents by the content urls
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
        # extract all the contents and resolve them by bs4
        htmls = self._extract_content(pages)
        soups = list()
        for html in htmls:
            soup = bs(html.text, 'lxml')
            soups.append(soup)
        return soups
    
    def show_titles(self, soups):
        # extract the titles of the contents
        titles = list()
        for soup in soups:
            title = soup.select('title')
            title = title[0].text
            titles.append(title)
        return titles
        