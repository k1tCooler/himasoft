'''
Created on 2017年10月20日
    天天美食
@author: dell
'''
from scrapy import Spider
from scrapy.http import Request
from ipproxytool.items import FoodBookItem
from scrapy import Selector
import re


class TtMeiShiBookSpider(Spider):
    '''爬取菜谱'''
    name = 'tt_mei_shi_book'
    download_delay = 0.5
    start_urls = [
        'http://www.ttmeishi.com/CaiXi/JiaChangCai/',
        'http://www.ttmeishi.com/CaiXi/ZhuShi/',
        'http://www.ttmeishi.com/CaiXi/LiangCai/',
        'http://www.ttmeishi.com/CaiXi/MeiWeiGaoDian/',
        'http://www.ttmeishi.com/CaiXi/ZhouTang/',
        'http://www.ttmeishi.com/CaiXi/YinPin/',
        'http://www.ttmeishi.com/CaiXi/ShiPu/',
        'http://www.ttmeishi.com/CaiXi/WeiBo/',
        'http://www.ttmeishi.com/CaiXi/YaoShan/',
        'http://www.ttmeishi.com/CaiXi/GanGuo/',
        'http://www.ttmeishi.com/CaiXi/SiJiaCai/',
        'http://www.ttmeishi.com/CaiXi/SuZhaiCai/',
        'http://www.ttmeishi.com/CaiXi/TianPinDianXin/',
        'http://www.ttmeishi.com/CaiXi/LuJiangCai/',
        'http://www.ttmeishi.com/CaiXi/NianYeFan/'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, meta={'need_proxy': True}, dont_filter=True)

    def parse(self, response):
        data = response.xpath(
            '//div[@class="content"]/ul[@class="cx_liebiao"]/li[@class="cx_liebiao_li"]').extract()
        # 循环菜谱解析并保存到数据库中
        for i in data:
            value_i = Selector(text=i)
            item = FoodBookItem()
            url = 'http://www.ttmeishi.com' + \
                value_i.xpath('//li/a/attribute::href').extract_first()
            item['ico_path'] = value_i.xpath(
                '//li/a/img/attribute::src').extract_first()
            if item['ico_path'].lower().find('http') < 0:
                item['ico_path'] = 'http://www.ttmeishi.com' + item['ico_path']
            item['name'] = value_i.xpath(
                '//li/a/text()').extract_first()
            print(url)
            content_req = Request(
                url, meta={'need_proxy': True, 'extra': item}, callback=self.parse_content, dont_filter=True)
            yield content_req
        '''解析下一页'''
        page = response.xpath(
            '//div[@class="pageNum"]/a[@class="pageon"]/text()').extract_first()
        if page:
            page = int(page) + 1
            next_page = re.sub('list[0-9]*.htm', '',
                               response.url) + 'list' + str(page) + '.htm'
            print(next_page)
            yield Request(next_page, meta={'need_proxy': True}, dont_filter=True)
        else:  # 获取不到页面内容则重新请求一次
            embed = response.xpath(
                '//embed/attribute::src').extract()  # 代理ip劫持网址时，重新发送请求
            if embed:
                yield Request(response.url, meta={'need_proxy': True}, dont_filter=True)

    def parse_content(self, response):
        item = response.meta['extra']
        main = response.xpath(
            '//div[@id="main"]/div[@id="content"]')
        if not main:
            embed = response.xpath(
                '//embed/attribute::src').extract()  # 代理ip劫持网址时，重新发送请求
            if embed:
                content_req = Request(
                    response.url, meta={'need_proxy': True, 'extra': item}, callback=self.parse_content, dont_filter=True)
                yield content_req
        else:
            item['img_paths'] = main.xpath(
                '//div[@class="c_img_show1"]/img/attribute::src').extract()
            item['img_paths'] = item['img_paths'] + main.xpath(
                '//div[@class="c_bz_img"]/img/attribute::src').extract()
            tds = main.xpath(
                '//table/tr/td[@class="c_leibie_sc"]').extract()
            item['cbfm_rel'] = []
            for td in tds:
                value_td = Selector(text=td)
                item['cbfm_rel'].append({'fm_name': value_td.xpath('(//a|//font)/text()').extract_first(),
                                         'fm_weight': value_td.xpath('//span/text()').extract_first()})
            item['username'] = '天天美食'

            step = main.xpath(
                '//div[@class="c_buzhou cbox"]/text()|//div[@class="c_buzhou cbox"]/h2/text()|//div[@class="c_bz_neirong"]/text()').extract()
            item['makestep'] = '\r\n'.join(step)
            yield item
