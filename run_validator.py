# -*- coding: utf-8 -*-
'''
    执行验证代理ip的爬虫
'''

import logging
import os
import subprocess
import sys
import scrapydo

from ipproxytool.spiders.validator.httpbin import HttpBinSpider

scrapydo.setup()


def validator():
    os.chdir(sys.path[0])

    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
        filename='log/validator.log',
        format='%(asctime)s: %(message)s',
        level=logging.DEBUG
    )
    
    validators = [
        HttpBinSpider,  # 必须
        # LagouSpider,
        # BossSpider,
        # LiepinSpider,
        # JDSpider,
        # DoubanSpider,
        # BBSSpider,
        # ZhiLianSpider,
        # AmazonCnSpider,
    ]

    process_list = []
    for validator in validators:
        popen = subprocess.Popen(
            ['python', 'run_spider.py', validator.name], shell=False)
        data = {
            'name': validator.name,
            'popen': popen,
        }
        process_list.append(data)


if __name__ == '__main__':
    validator()
