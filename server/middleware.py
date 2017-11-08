'''
Created on 2017年10月20日

@author: dell
'''
import json

import requests
from scrapy.exceptions import IgnoreRequest

from sql import SqlManager
import utils
import random
import logging


class ProxyMiddleWare(object):
    """docstring for ProxyMiddleWare"""

    def process_request(self, request, spider):
        if 'need_proxy' in request.meta.keys():
            if request.meta['need_proxy']:
                proxy = self.get_random_proxy()
                '''对request对象加上proxy'''
                if (proxy != None):
                    request.meta['item'] = proxy.id
                    proxy = 'http://%s:%s' % (proxy.ip, proxy.port)
                    print("this is request ip:" + proxy)
                    request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        if 'need_proxy' in request.meta.keys():
            if request.meta['need_proxy']:
                # 如果返回的response状态不是200，重新生成当前request对象
                if response.status != 200:
                    return request
        return response

    def process_exception(self, request, exception, spider):
        if 'need_proxy' in request.meta.keys():
            if request.meta['need_proxy']:
                return request

    def get_random_proxy(self):
        '''随机从文件中读取proxy'''
        sql = SqlManager()
        proxy = sql.get_proxy_random('httpbin')
        return proxy


class UserAgentMiddleWare(object):
    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('USER_AGENT')
        )

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)
        print('current User-Agent: ' + agent)
        request.headers['User-Agent'] = agent


if __name__ == '__main__':
    proxy = ProxyMiddleWare().get_random_proxy()
    utils.log(proxy)


class ProxyKangMiddleware():
    def __init__(self, proxy_url):
        self.logger = logging.getLogger(__name__)
        self.proxy_url = proxy_url

    def _get_random_url(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                return response.text
        except ConnectionError:
            return None

    def process_request(self, request, spider):
        if spider.name == 'xiachufang':
            proxy_url = self._get_random_url()
            if proxy_url:
                request.meta['proxy'] = proxy_url
                self.logger.debug('Using Proxy_Url ' + json.dumps(proxy_url))
            else:
                self.logger.debug('No Valid Proxy_Url')
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_url='http://127.0.0.1:5000/get'
            # crawler.settings.get('proxy_url')
        )

    def process_response(self, request, response, spider):
        if spider.name == 'xiachufang':
            if response.status in [429]:
                try:
                    self.logger.warning('Proxy_Url UnValid')
                    proxy_url = self._get_random_url()
                    request.meta['proxy'] = proxy_url
                    self.logger.debug('Using Proxy_url' + json.dumps(proxy_url))
                    return request
                except Exception:
                    raise IgnoreRequest
            elif response.status in [414]:
                return request
            else:
                return response
        pass
