'''
Created on 2017年10月20日
    中国菜谱网
@author: dell
'''
from scrapy import Spider
from scrapy.http import Request
from ipproxytool.items import FoodMaterialItem
from ipproxytool.items import FoodBookItem
from scrapy import Selector


class ChinaCaiPuMaterialSpider(Spider):
    '''爬取食材信息'''
    name = 'china_cai_pu_material'
    download_delay = 0.5
    start_urls = [
        'http://www.chinacaipu.com/shicai/',
    ]

    def __init__(self, name=None, **kwargs):
        super(ChinaCaiPuMaterialSpider, self).__init__(name, **kwargs)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0",
        }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, meta={'need_proxy': True}, dont_filter=True)

    def parse(self, response):
        food_materials = response.xpath(
            '//div[@class="fd_main"]/div/div').extract_first()
        val = Selector(text=food_materials).re('<strong[\s\S]*?</dl>')
        for i in val:
            value_i = Selector(text=i)
            content = value_i.xpath('//dl/dd/a').extract()
            for j in content:
                item = FoodMaterialItem()
                item['fcls_name'] = value_i.xpath(
                    '//strong/text()').extract_first()
                item['scls_name'] = value_i.xpath(
                    '//dl/dt/text()').extract_first()
                value_j = Selector(text=j)
                item['name'] = value_j.xpath('//a/text()').extract_first()
                item['name_jc'] = item['name']
                item['ico_path'] = value_j.css(
                    'img::attr(src)').extract_first()
                item['username'] = '中国食谱网'
                content_url = value_j.css('a::attr(href)').extract_first()
                content_req = Request(
                    content_url, meta={'need_proxy': True, 'extra': item}, callback=self.parse_content, dont_filter=True)
                yield content_req

    def parse_content(self, response):
        item = response.meta['extra']
        item['desc'] = response.xpath(
            '//div[@class="n_sp_main_info"]/p/text()').extract_first()
        yield item


class ChinaCaiPuBookSpider(Spider):
    '''爬取菜谱'''
    name = 'china_cai_pu_book'
    download_delay = 0.1
    start_urls = [
        'http://www.chinacaipu.com/menu/chinacaipu/',
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, meta={'need_proxy': True}, dont_filter=True)

    def parse(self, response):
        data = response.xpath(
            '//div[@class="c_con3"]/ul/li').extract()
        # 循环菜谱解析并保存到数据库中
        for i in data:
            value_i = Selector(text=i)
            item = FoodBookItem()
            url = value_i.xpath('//div/a/attribute::href').extract_first()
            item['ico_path'] = value_i.xpath(
                '//div/a/img/attribute::src').extract_first()
            item['name'] = value_i.xpath(
                '//strong/a[last()]/text()').extract_first()
            print(url)
            content_req = Request(
                url, meta={'need_proxy': True, 'extra': item}, callback=self.parse_content, dont_filter=True)
            yield content_req
        '''解析下一页'''
        page = response.xpath(
            '//div[@class="page"]/a[last()]/attribute::href').extract_first()
        if page:
            next_page = 'http://www.chinacaipu.com' + page
            next_page_text = response.xpath(
                '//div[@class="page"]/a[last()]/text()').extract_first()
            if(next_page_text == '下一页'):
                print(next_page)
                yield Request(next_page, meta={'need_proxy': True}, dont_filter=True)
        else:  # 获取不到页面内容则重新请求一次
            embed = response.xpath(
                '//embed/attribute::src').extract()  # 代理ip劫持网址时，重新发送请求
            if embed:
                yield Request(response.url, meta={'need_proxy': True}, dont_filter=True)

    def parse_content(self, response):
        item = response.meta['extra']
        tds = response.xpath(
            '//div[@class="cp-show-main"]/table/tr/td').extract()
        item['cbfm_rel'] = []
        for td in tds:
            value_td = Selector(text=td)
            item['cbfm_rel'].append({'fm_name': value_td.xpath('//span/text()').extract_first(),
                                     'fm_weight': value_td.xpath('//i/text()').extract_first()})
        step = response.xpath(
            '//div[@class="cp-show-main-step"]/div/div/div[@class="summary"]/text()').extract()
        item['username'] = '中国食谱网'
        if step:
            trick = response.xpath(
                '//div[@class="cp-show-main-trick"][1]/p/text()').extract()
            item['makestep'] = '\r\n'.join(
                step + trick).replace('\u3000', '').replace('\xa0', '').replace('\u200b', '')
            item['img_paths'] = response.xpath(
                '//div[@class="cp-show-main-step"]/div/div/img/attribute::src').extract()
            yield item
        else:
            step = response.xpath(
                '//div[@id="content"]/p/text()').extract()
            if step:
                item['makestep'] = '\r\n'.join(step).replace(
                    '\u3000', '').replace('\xa0', '').replace('\u200b', '')
                item['img_paths'] = response.xpath(
                    '//div[@id="content"]/p/strong/img/attribute::src').extract() + response.xpath(
                    '//div[@id="content"]/p/img/attribute::src').extract()
                yield item
            else:  # 获取不到内容重新发起请求
                embed = response.xpath(
                    '//embed/attribute::src').extract()  # 代理ip劫持网址时，重新发送请求
                if embed:
                    content_req = Request(
                        response.url, meta={'need_proxy': True, 'extra': item}, callback=self.parse_content, dont_filter=True)
                    yield content_req
