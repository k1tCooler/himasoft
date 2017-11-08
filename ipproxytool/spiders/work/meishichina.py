# -*- coding: utf-8 -*-
import re

import logging
import scrapy
from scrapy import Selector
from scrapy.http import Request

from ipproxytool.items import FoodBookItem


class MeishichinaSpider(scrapy.Spider):
    name = 'meishichina'
    allowed_domains = ['http://www.meishichina.com/']
    start_url = 'http://home.meishichina.com/recipe-type.html'
    download_delay = 1
    search_urls = []
    local_search = 0
    page_flag = True
    page = 4
    re_try = 0

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'home.meishichina.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    def start_requests(self):
        yield Request(self.start_url, headers=self.headers, meta={'need_proxy': True}, callback=self.parse_index,
                      dont_filter=True)

    def parse_index(self, response):
        if not self.search_urls:
            self.search_urls = response.xpath('//div[@class="category_sub clear"]//ul//li/a/@href').extract()

        if self.local_search + 1 == len(self.search_urls):
            self.local_search = 0

        if self.search_urls[self.local_search]:
            search_url = self.search_urls[self.local_search]
            if '.html' in search_url:
                if self.page >= 2:
                    p = re.compile(r'page-(.*?).html')
                    search_url = p.sub('page-{page}.html', search_url).format(page=self.page)
                    yield Request(search_url, headers=self.headers, meta={'need_proxy': True},
                                  callback=self.parse_search,
                                  dont_filter=True)
                else:
                    yield Request(search_url, headers=self.headers, meta={'need_proxy': True},
                                  callback=self.parse_search,
                                  dont_filter=True)
            else:
                search_url = search_url + 'page/{page}/'.format(page=self.page)
                yield Request(search_url, headers=self.headers, meta={'need_proxy': True},
                              callback=self.parse_search,
                              dont_filter=True)

    def parse_search(self, response):
        recipe_urls = response.xpath('//div[@class="detail"]//h2//a/@href').extract()
        next_page = response.xpath('//div[@class="ui-page mt10"]').extract_first()
        search_flag = True
        if recipe_urls:
            for i in range(len(recipe_urls)):
                yield Request(recipe_urls[i], headers=self.headers, meta={'need_proxy': True},
                              callback=self.parse_recipe, dont_filter=True)
                if next_page and '下一页' not in next_page:
                    search_flag = False
                    self.local_search += 1
            if search_flag == False:
                self.page = 1
            else:
                self.page += 1
            yield Request(self.start_url, headers=self.headers, meta={'need_proxy': True}, callback=self.parse_index,
                          dont_filter=True)
            self.re_try = 0
        else:
            if self.re_try <= 3:
                yield Request(response.url, headers=self.headers, meta={'need_proxy': True}, callback=self.parse_search,
                              dont_filter=True)
                self.re_try += 1
            else:
                self.local_search += 1
                self.page = 1
                yield Request(self.start_url, headers=self.headers, meta={'need_proxy': True},
                              callback=self.parse_index,
                              dont_filter=True)

    def parse_recipe(self, response):
        fooditem = FoodBookItem()

        # 菜肴名称
        name = response.xpath('//a[@id="recipe_title"]/text()').extract_first()
        if name:
            fooditem['name'] = name.replace('\n', '').strip()

            # 烹饪步骤
            makesteps = response.xpath('//div[@class="recipeStep_word"]/text()').extract()

            i = 1
            val = ''
            for makestep in makesteps:
                makestep = str(i) + '、' + makestep + '\r\n'
                val = val + makestep
                i += 1

            try:
                # python UCS-4 build的处理方式
                highpoints = re.compile(u'[\U00010000-\U0010ffff]')
            except re.error:
                # python UCS-2 build的处理方式
                highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
            resovle_value = highpoints.sub(u'??', val).replace('??', '')
            fooditem['makestep'] = resovle_value.replace('<br>', '')

            # 菜肴缩略图
            fooditem['ico_path'] = response.xpath(
                '//div[@class="recipe_De_imgBox"]/a/img/@src').extract_first()

            # 菜肴图片列表
            fooditem['img_paths'] = response.xpath('//div[@class="recipeStep_img"]/img/@src').extract()

            # 菜肴食材
            cbfm_rels = response.xpath('//div[@class="recipeCategory_sub_R clear"]/ul/li').extract()
            fooditem['cbfm_rel'] = []
            for cbfm_rel in cbfm_rels:
                selector = Selector(text=cbfm_rel)
                fm_name = selector.xpath('//span[@class="category_s1"]').re_first("<b>(.*?)</b>")
                if fm_name:
                    fm_name = fm_name.replace('\n', '').strip()

                fm_weight = selector.xpath('//span[@class="category_s2"]//text()').extract_first()
                if fm_weight:
                    fm_weight = fm_weight.replace('\n', '').strip()

                fooditem['cbfm_rel'].append({'fm_name': fm_name,
                                             'fm_weight': fm_weight})
            fooditem['username'] = response.url
            yield fooditem
            self.re_try = 0
        else:
            if self.re_try <= 3:
                yield Request(response.url, headers=self.headers, meta={'need_proxy': True},
                              callback=self.parse_recipe, dont_filter=True)

                self.re_try += 1


        print('local_search~~~~~~~~~~~~~~~~~~~~~~~~~~~' + str(self.local_search))
