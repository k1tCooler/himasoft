# -*- coding: utf-8 -*-

from scrapy import Spider, Selector
from scrapy.http import Request

from ipproxytool.items import FoodBookItem


class XiachufangSpider(Spider):
    name = 'xiachufang'
    allowed_domains = ['www.xiachufang.com']
    start_url = 'http://www.xiachufang.com/'
    search_url = 'http://www.xiachufang.com{url}?page={page}'
    recipe_url = 'http://www.xiachufang.com{url}'
    download_delay = 1
    page = 0
    search_limit = 0

    def start_requests(self):
        # yield Request(self.start_url,meta={'need_proxy': True}, callback=self.parse_leftcats, dont_filter=True)
        yield Request('http://www.xiachufang.com/category/40071/?page=94', meta={'need_proxy': True}, callback=self.parse_recipe,
                      dont_filter=True)

    def parse_leftcats(self, response):
        urls = response.css('.left-panel ul li .homepage-cat-name::attr(href)').extract()
        if urls:
            self.page += 1
            for url in urls:
                yield Request(self.search_url.format(url=url, page=self.page), meta={'need_proxy': True},callback=self.parse_search, dont_filter=True)

    def parse_search(self, response):
        urls = response.xpath('//div[@class="normal-recipe-list"]/ul/li/a/@href').extract()
        if urls:
            for url in urls:
                print(self.recipe_url.format(url=url))
                yield Request(self.recipe_url.format(url=url), meta={'need_proxy': True},callback=self.parse_recipe, dont_filter=True)
            yield Request(self.start_url, meta={'need_proxy': True},callback=self.parse_leftcats, dont_filter=True)

    def parse_recipe(self, response):
        fooditem = FoodBookItem()

        # 菜肴名称
        name = response.css('.page-title::text').extract_first()
        if name:
            fooditem['name'] = name.replace('\n', '').strip()

        # 烹饪步骤
        makesteps = response.xpath('//div[@class="steps"]/ol/li[@class="container"]').re("class=\"text\".*?>(.*?)</p>")

        i = 1
        val = ''
        for makestep in makesteps:
            makestep = str(i) + '、' + makestep + '\r\n '
            val = val + makestep
            i += 1
        fooditem['makestep'] = val.replace('<br>', '')

        # 菜肴缩略图
        fooditem['ico_path'] = response.xpath(
            '//div[@class="cover image expandable block-negative-margin"]/img/@src').extract_first()

        # 菜肴图片列表
        fooditem['img_paths'] = response.xpath('//div[@class="steps"]/ol/li[@class="container"]/img/@src').extract()

        # 菜肴食材
        cbfm_rels = response.css('.ings table tr').extract()
        fooditem['cbfm_rel'] = []
        for cbfm_rel in cbfm_rels:
            selector = Selector(text=cbfm_rel)
            fm_name = selector.css('.name::text').extract_first()
            if fm_name and fm_name.replace('\n', '').strip():
                fm_name = fm_name.replace('\n', '').strip()
            else:
                fm_name = selector.css('.name a::text').extract_first()
                if fm_name:
                    fm_name = fm_name.replace('\n', '').strip()

            fm_weight = selector.css('.unit::text').extract_first()
            if fm_weight:
                fm_weight = fm_weight.replace('\n', '').strip()

            fooditem['cbfm_rel'].append({'fm_name': fm_name,
                                         'fm_weight': fm_weight})
        fooditem['username'] = response.url
        yield fooditem
