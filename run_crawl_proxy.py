# -*- coding: utf-8 -*-
'''
    执行爬虫抓取代理ip
'''

import logging
import os
import sys
import scrapydo
import utils
import config

from sql import SqlManager
from ipproxytool.spiders.proxy.xicidaili import XiCiDaiLiSpider
from ipproxytool.spiders.proxy.sixsixip import SixSixIpSpider
from ipproxytool.spiders.proxy.ip181 import IpOneEightOneSpider
from ipproxytool.spiders.proxy.kuaidaili import KuaiDaiLiSpider
from ipproxytool.spiders.proxy.proxylistplus import ProxylistplusSpider
from ipproxytool.spiders.proxy.freeproxylists import FreeProxyListsSpider
from ipproxytool.spiders.proxy.usproxy import UsProxySpider
from ipproxytool.spiders.proxy.proxydb import ProxyDBSpider
from ipproxytool.spiders.validator.httpbin import HttpBinSpider

scrapydo.setup()


def run():
    os.chdir(sys.path[0])

    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
        filename='log/crawl_proxy.log',
        format='%(levelname)s %(asctime)s: %(message)s',
        level=logging.DEBUG
    )

    sql = SqlManager()

    spiders = [
        XiCiDaiLiSpider,  # 西刺免费代理IP
        SixSixIpSpider,  # 被网管禁止了
        IpOneEightOneSpider,  # ip181
        KuaiDaiLiSpider,  # 快代理
        # GatherproxySpider, # 此网站已无法访问了
        # HidemySpider, # 此网站已无法访问了
        ProxylistplusSpider,  # 国外ProxyList+
        FreeProxyListsSpider,  # 被网管禁止了
        # PeulandSpider,  # 此网站已无法访问了
        UsProxySpider,  # 被网管禁止了
        ProxyDBSpider,  # proxydb,使用scrapy_splash来解析javascript内容生成静态网页
        # ProxyRoxSpider, # 此网站已无法访问了

        HttpBinSpider,  # 必须  验证ip是否有效
    ]

    utils.log(
        '*******************run_crawl_proxy spider start...*******************')
    sql.delete_old(config.free_ipproxy_table, 0.5)
    for spider in spiders:
        scrapydo.run_spider(spider_cls=spider, timeout=10 * 3600)
    utils.log(
        '*******************run_crawl_proxy spider finish...*******************')


if __name__ == '__main__':
    run()
