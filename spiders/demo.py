# coding: utf-8
'''
filename: 
author: mr_zys
email: mrzysv5@sina.com
description: 无语
'''
from spiders.spiders import Spider
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import time
import traceback
from Queue import Queue
import re
import json

q_req = Queue()
q_res = Queue()

class BaseSpider(Spider):
    def parse(self, req, response):
        res = response.read()
        bs = BeautifulSoup(re.sub('\n|\t', '', res))
        menu_sub = bs.find_all("div", attrs={"class":"menu_sub dn"})
        cnt = 0
        for menu in menu_sub:
            for child in menu:
                if isinstance(child, NavigableString):
                    continue
                if child.name == 'dl':
                    dd = child.find("dd")
                    for a in dd.find_all('a'):
                        if cnt > 10:
                            break
                        cnt += 1
                        kd = a.get_text().strip()
                        first = 'true'
                        pn = 1
                        kd = kd.encode('utf8')
                        data = 'first=' + first + '&pn=' + str(pn) + '&kd=' + kd
                        url = 'http://www.lagou.com/jobs/positionAjax.json'
                        self.request(url, self.get_position, data=data)

    def get_position(self, req, response):
        py_data = json.loads(response.read())
        result = py_data['content']['result']
        for r in result:
            yield r['companyShortName']


def main():
    st = time.time()
    urls = [
    # 'http://www.python.org',
    # 'http://www.sina.com.cn',
    # 'http://www.baidu.com',
    # 'http://www.mr-zys.top',
    # 'http://www.sohu.com',
    # 'http://www.qq.com',
    # 'http://www.163.com'
    'http://www.lagou.com'
    ]
    spider = BaseSpider(q_req=q_req, q_res=q_res, threads=4)
    for url in urls:
        spider.push(url)
    while spider.task_left():
        item = spider.pop()
        print item
    et = time.time()
    print 'tot time %f' % (et - st)

if __name__ == '__main__':
        main()




