# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from ipproxytool.spiders.work.mysql_recipes import MySqlRecipes


class IpproxytoolPipeline(object):
    def process_item(self, item, spider):
        print(item)
        if spider.name == 'china_cai_pu_material':
            mysql = MySqlRecipes()
            mysql.insert_foodmaterial(item)
            print('=======================ChinaCaiPuMaterial==========================')
        elif spider.name == 'china_cai_pu_book':
            mysql = MySqlRecipes()
            mysql.insert_food_book(item)
            print('=======================ChinaCaiPuBook==========================')
        elif spider.name == 'tt_mei_shi_book':
            mysql = MySqlRecipes()
            mysql.insert_food_book(item)
            print('=======================TtMeiShiBook==========================')
        elif(spider.name == 'xiachufang'):
            mysql = MySqlRecipes()
            mysql.insert_food_book(item)
            print('=======================XiaChuFangBook==========================')
        elif (spider.name == 'meishichina'):
            mysql = MySqlRecipes()
            mysql.insert_food_book(item)
            print('=======================MeiShiChinaBook==========================')
        return item
