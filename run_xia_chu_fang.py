# -*- coding: utf-8 -*-
'''
    下厨房
'''

import logging
import os

import scrapydo

from ipproxytool.spiders.work.xiachufang import XiachufangSpider

scrapydo.setup()


def work():

    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
        filename='log/xia_chu_fang.log',
        format='%(asctime)s: %(message)s',
        level=logging.INFO
    )

    works = [
        XiachufangSpider,  # 下厨房
    ]

    for work in works:
        scrapydo.run_spider(spider_cls=work, timeout=24 * 3600)


if __name__ == '__main__':
    work()
