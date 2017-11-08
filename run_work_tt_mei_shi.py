# -*- coding: utf-8 -*-
'''
    天天美食网
'''

import logging
import os
import scrapydo

from ipproxytool.spiders.work.ttmeishi import TtMeiShiBookSpider

scrapydo.setup()


def work():

    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
        filename='log/tt_mei_shi.log',
        format='%(asctime)s: %(message)s',
        level=logging.INFO
    )

    works = [
        TtMeiShiBookSpider,  # 天天美食
    ]

    for work in works:
        scrapydo.run_spider(spider_cls=work, timeout=24 * 3600)


if __name__ == '__main__':
    work()
