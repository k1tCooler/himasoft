# -*- coding: utf-8 -*-
'''
    下厨房
'''

import logging
import os

import scrapydo

from ipproxytool.spiders.work.meishichina import MeishichinaSpider

scrapydo.setup()


def work():

    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
        filename='log/mei_shi_china.log',
        format='%(asctime)s: %(message)s',
        level=logging.INFO
    )

    works = [
        MeishichinaSpider,  # 下厨房
    ]

    for work in works:
        scrapydo.run_spider(spider_cls=work, timeout=24 * 3600)


if __name__ == '__main__':
    work()
