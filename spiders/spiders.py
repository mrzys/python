# coding: utf-8
'''
filename: spiders.py
author: mr_zys
email: mrzysv5@sina.com
description: 
'''
import urllib2
import traceback
from bs4 import BeautifulSoup
from threading import Thread,Lock,current_thread
import time
from Queue import Queue

import urllib2
from gzip import GzipFile
from StringIO import StringIO
import types

class ContentEncodingProcessor(urllib2.BaseHandler):
  """A handler to add gzip capabilities to urllib2 requests """

  # add headers to requests
  def http_request(self, req):
    req.add_header("Accept-Encoding", "gzip")
    req.add_header("User-agent", "Mozilla/5.0");
    return req

  # decode
  def http_response(self, req, resp):
    old_resp = resp
    # gzip
    if resp.headers.get("content-encoding") == "gzip":
        gz = GzipFile(
                    fileobj=StringIO(resp.read()),
                    mode="r"
                  )
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
        resp.msg = old_resp.msg
    # deflate
    if resp.headers.get("content-encoding") == "deflate":
        gz = StringIO( deflate(resp.read()) )
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)  # 'class to add info() and
        resp.msg = old_resp.msg
    return resp

# deflate support
import zlib
def deflate(data):   # zlib only provides the zlib compress format, not the deflate format;
  try:               # so on top of all there's this workaround:
    return zlib.decompress(data, -zlib.MAX_WBITS)
  except zlib.error:
    return zlib.decompress(data)

class Spider:

    def __init__(self, q_req=None, q_res=None, threads=4):
        encoding_support = ContentEncodingProcessor
        self.opener = urllib2.build_opener(encoding_support, urllib2.HTTPHandler)
        self.lock = Lock() #线程锁
        self.q_req = q_req or Queue() #任务队列
        self.q_res = q_res or Queue() #完成队列
        self.threads = threads # 线程数
        for i in xrange(self.threads):
            t = Thread(target=self.get_page)
            t.setDaemon(True)
            t.start()
        self.running = 0

    def __del__(self):
        self.q_req.join()
        self.q_res.join()

    def push(self,req):
        '''
        向任务队列中添加url，也可以是`urllib2.Request`对象
        '''
        if isinstance(req, str):
            self.q_req.put((self.parse, req))
        else:
            self.q_req.put(req)

    def pop(self):
        return self.q_res.get()


    def get_page(self):
        '''
        获取页面的方法，线程执行的就是该方法
        '''
        while True:
            method,req = self.q_req.get()
            with self.lock:
                self.running += 1
            try:
                res = self.opener.open(req)
            except:
                res = ''
                traceback.print_exc()
            result = method(req, res)
            if isinstance(result, types.GeneratorType):
                for r in result:
                    self.q_res.put(r)
            elif isinstance(result, str):
                self.q_res.put(result)
            elif isinstance(result, unicode):
                self.q_res.put(result)
            with self.lock:
                self.running -= 1
            self.q_req.task_done()

    def task_left(self):
        '''
        所有队列的size，加上刚取出的
        '''
        return self.q_res.qsize() + self.q_req.qsize() + self.running

    def request(self, url, method, data=None):
        '''
        将url和方法绑定放在队列中，这样才可以根据url调用不同的方法
        '''
        if data:
            req = urllib2.Request(url=url, data=data)
        self.q_req.put((method, req))


class BaseSpider(Spider):
    def parse(self, req, response):
        try:
            soup = BeautifulSoup(response)
            #print '%s title:' % (req)
            a = soup.find('title')
            b = a.get_text()
            return b
        except:
            traceback.print_exc()

def main():
    st = time.time()
    urls = [
    'http://www.python.org',
    'http://www.sina.com.cn',
    'http://www.baidu.com',
    'http://www.mr-zys.top',
    'http://www.sohu.com',
    'http://www.qq.com',
    'http://www.163.com'
    ]
    spider = BaseSpider(threads=4)
    for url in urls:
        print url
        spider.push(url)
    print 'taskleft %d' % spider.task_left()
    while spider.task_left():
        r = spider.pop()
        print r
    et = time.time()
    print 'tot time %f' % (et - st)

if __name__ == '__main__':
        main()



