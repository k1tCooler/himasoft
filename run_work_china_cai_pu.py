# -*- coding: utf-8 -*-
'''
    中国食谱网
'''

import logging
import os
import scrapydo

from ipproxytool.spiders.work.chinacaipu import ChinaCaiPuMaterialSpider
from ipproxytool.spiders.work.chinacaipu import ChinaCaiPuBookSpider

scrapydo.setup()


def work():
    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
        filename='log/china_cai_pu.log',
        format='%(asctime)s: %(message)s',
        level=logging.INFO
    )

    works = [
        ChinaCaiPuMaterialSpider,  # 中国食谱网食材
        ChinaCaiPuBookSpider,  # 中国食谱网菜肴
    ]

    for work in works:
        scrapydo.run_spider(spider_cls=work, timeout=10 * 3600)


if __name__ == '__main__':
    work()
