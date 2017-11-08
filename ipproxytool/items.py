# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IpproxytoolItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class FoodBookItem(scrapy.Item):
    # 菜谱
    name = scrapy.Field()  # 菜肴名称
    makestep = scrapy.Field()  # 烹饪步骤
    ico_path = scrapy.Field()  # 菜肴缩略图
    img_paths = scrapy.Field()  # 菜肴图片列表
    cbfm_rel = scrapy.Field()  # 菜肴食材
    username = scrapy.Field()  # 来源网站


class FoodMaterialItem(scrapy.Item):
    # 食材
    fcls_name = scrapy.Field()  # 大类名称
    scls_name = scrapy.Field()  # 亚类名称
    name = scrapy.Field()  # 食材名称
    name_jc = scrapy.Field()  # 食材简称
    desc = scrapy.Field()  # 食材描述
    ico_path = scrapy.Field()  # 食材缩略图
    username = scrapy.Field()  # 来源网站
