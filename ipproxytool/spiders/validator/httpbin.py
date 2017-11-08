# -*- coding: utf-8 -*-
'''
    验证代理ip是否有效
'''
import json
import time
import requests
import config

from scrapy import Request
from .validator import Validator


class HttpBinSpider(Validator):
    name = 'httpbin'
    concurrent_requests = 16

    def __init__(self, name=None, **kwargs):
        super(HttpBinSpider, self).__init__(name, **kwargs)
        self.timeout = 20
        self.urls = [
            'http://httpbin.org/get?show_env=1',
            'https://httpbin.org/get?show_env=1',
        ]
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Host": "httpbin.org",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0"
        }
        self.origin_ip = ''
        self.init()

    def init(self):
        super(HttpBinSpider, self).init()
        r = requests.get(url=self.urls[0], timeout=20)
        data = json.loads(r.text)
        self.origin_ip = data.get('origin', '')
        self.log('origin ip:%s' % self.origin_ip)

    def start_requests(self):
        # 统计访问过httpbin的有效代理ip数量
        count = self.sql.get_proxy_count(self.name)
        # 统计抓取到的ip数量
        count_free = self.sql.get_proxy_count(config.free_ipproxy_table)

        # 获取访问过httpbin的有效ip的ids列表
        ids = self.sql.get_proxy_ids(self.name)
        # 获取所有ip的ids列表
        ids_free = self.sql.get_proxy_ids(config.free_ipproxy_table)

        for i in range(0, count + count_free):
            # 默认从访问过httpbin有效的ip中取，如果没有，则从抓取到的代理ip池中取
            table = self.name if (i < count) else config.free_ipproxy_table
            ip_id = ids[i] if i < count else ids_free[i - len(ids)]

            proxy = self.sql.get_proxy_with_id(table, ip_id)  # 查询代理ip地址
            if proxy == None:
                continue

            for url in self.urls:
                https = 'yes' if 'https' in url else 'no'

                yield Request(
                    url=url,
                    headers=self.headers,
                    dont_filter=True,
                    priority=0 if https == 'yes' else 10,
                    meta={
                        'cur_time': time.time(),
                        'download_timeout': self.timeout,
                        'proxy_info': proxy,
                        'table': table,
                        'https': https,
                        'proxy': 'http://%s:%s' % (proxy.ip, proxy.port),
                        'vali_count': proxy.vali_count,
                    },
                    callback=self.success_parse,
                    errback=self.error_parse,
                )

    def success_parse(self, response):
        proxy = response.meta.get('proxy_info')
        table = response.meta.get('table')
        proxy.https = response.meta.get('https')

        self.save_page(proxy.ip, response.body)

        if self.success_content_parse(response):
            proxy.speed = time.time() - response.meta.get('cur_time')
            proxy.vali_count += 1
            self.log('proxy_info:%s' % (str(proxy)))

            if proxy.https == 'no':
                data = json.loads(response.body)
                origin = data.get('origin')
                headers = data.get('headers')
                x_forwarded_for = headers.get('X-Forwarded-For', None)
                x_real_ip = headers.get('X-Real-Ip', None)
                via = headers.get('Via', None)

                if self.origin_ip in origin:
                    proxy.anonymity = 3
                elif via is not None:
                    proxy.anonymity = 2
                elif x_forwarded_for is not None and x_real_ip is not None:
                    proxy.anonymity = 1

                if table == self.name:
                    if proxy.speed > self.timeout:
                        self.sql.del_proxy_with_id(
                            table_name=table, id=proxy.id)
                    else:
                        self.sql.update_proxy(table_name=table, proxy=proxy)
                else:
                    # 少于20秒插入记录
                    if proxy.speed < self.timeout:
                        self.sql.insert_proxy(
                            table_name=self.name, proxy=proxy)
            else:
                self.sql.update_proxy(table_name=table, proxy=proxy)

        self.sql.commit()

    def error_parse(self, failure):
        request = failure.request
        self.log('error_parse value:%s url:%s meta:%s' %
                 (failure.value, request.url, request.meta))
        https = request.meta.get('https')
        if https == 'no':
            table = request.meta.get('table')
            proxy = request.meta.get('proxy_info')
            # 删除出错的记录
            self.sql.del_proxy_with_id(table_name=table, id=proxy.id)
