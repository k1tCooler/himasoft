#!/usr/bin/python

from scrapy import cmdline
name = 'meishichina'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())