# -*- coding: utf-8 -*-
'''
    爬取代理ip的程序入口
'''

import logging
import os
import sys
import subprocess

if __name__ == '__main__':

    # 进入当前项目目录
    os.chdir(sys.path[0])

    if not os.path.exists('log'):
        os.makedirs('log')

    # 日志配置
    logging.basicConfig(
        filename='log/ipproxy.log',
        format='%(asctime)s: %(message)s',
        level=logging.INFO
    )

    # 子进程执行命令
    # 爬取ip地址并过滤保存到httpbin表中
    subprocess.Popen(['python', 'run_crawl_proxy.py'])
    # 爬取中国食谱网数据
    subprocess.Popen(['python', 'run_work_china_cai_pu.py'])
    # 爬取天天美食数据
    subprocess.Popen(['python', 'run_work_tt_mei_shi.py'])