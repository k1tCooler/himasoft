# -*- coding: utf-8 -*-

import logging
import time
import pymysql

from ipproxytool import settings
from util.id_generator import IDGenerator


class MySqlRecipes:
    def __init__(self):
        self.conn = pymysql.connect(
            host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_DBNAME, port=settings.MYSQL_PORT, charset=settings.MYSQL_CHARSET)
        self.cursor = self.conn.cursor()

    def insert_foodmaterial(self, item):
        try:
            names = self.select_foodmaterial(item['name'])
            if not names:
                command = ("INSERT  INTO pub_foodmaterial_tmp"
                           "(FM_FCLS_NAME, FM_SCLS_NAME, FM_NAME, FM_NAME_JC, FM_DESC, ICO_PATH, STATUS, LAST_MODI_USERNAME, LAST_MODI_TIME) "
                           "VALUES(%s, %s, %s, %s, %s, %s, '0', %s, %s)")
                data = (item['fcls_name'], item['scls_name'], item['name'], item['name_jc'],
                        item['desc'], item['ico_path'], item['username'], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                self.cursor.execute(command, data)
                self.commit()
                return True
        except Exception as e:
            logging.exception('mysql insert_foodmaterial exception msg:%s' % e)
            return False

    def select_foodmaterial(self, name):
        try:
            command = "SELECT FM_NAME FROM pub_foodmaterial WHERE FM_NAME = '{0}' " \
                      "UNION ALL SELECT FM_NAME FROM pub_foodmaterial_tmp WHERE FM_NAME = '{0}' ". format(
                          name)
            result = self.query(command)
            data = [{'name': item[0]} for item in result]
            return data
        except Exception as e:
            logging.exception('mysql select_foodmaterial exception msg:%s' % e)
        return []

    def insert_food_book(self, item):
        try:
            names = self.select_food_book(item['name'])
            if not names:
                fb_id = IDGenerator.get_id()
                command = ("INSERT  INTO pub_food_book_tmp"
                           "(FB_ID,FB_NAME, FB_MAKESTEP, ICO_PATH, STATUS, LAST_MODI_USERNAME, LAST_MODI_TIME) "
                           "VALUES(%s,%s, %s, %s, '0', %s, %s)")
                data = (fb_id, item['name'], item['makestep'], item['ico_path'], item['username'], time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

                command2 = ("INSERT  INTO pub_fb_image_tmp"
                            "(FB_ID, FB_IMAGE) "
                            "VALUES(%s, %s)")
                list2 = []
                for img_path in item['img_paths']:
                    data2 = (fb_id, img_path)
                    list2.append(data2)

                command3 = ("INSERT  INTO pub_cbfm_rel_tmp"
                            "(FB_ID, FM_NAME, FM_WEIGHT) "
                            "VALUES(%s, %s, %s)")
                list3 = []
                for one in item['cbfm_rel']:
                    data3 = (fb_id, one['fm_name'], one['fm_weight'])
                    list3.append(data3)

                self.cursor.execute(command, data)
                if list2:
                    self.cursor.executemany(command2, list2)
                if list3:
                    self.cursor.executemany(command3, list3)
                self.commit()
                return True
        except Exception as e:
            logging.exception('mysql insert_food_book exception msg:%s' % e)
            return False

    def select_food_book(self, name):
        try:
            command = "SELECT FB_NAME FROM pub_food_book WHERE FB_NAME = '{0}' " \
                      "UNION ALL SELECT FB_NAME FROM pub_food_book_tmp WHERE FB_NAME = '{0}' ". format(
                          name)
            result = self.query(command)
            if result:
                data = [{'name': item[0]} for item in result]
            else:
                data = []
            return data
        except Exception as e:
            logging.exception('mysql select_food_book exception msg:%s' % e)
        return []

    def update_proxy(self, table_name, proxy):
        try:
            command = "UPDATE {table_name} set https='{https}', speed={speed}, " \
                      "vali_count={vali_count}, anonymity = {anonymity},save_time={save_time} " \
                      "where id={id};".format(
                          table_name=table_name, https=proxy.https,
                          speed=proxy.speed, id=proxy.id, vali_count=proxy.vali_count, anonymity=proxy.anonymity,
                          save_time='NOW()')
            logging.debug('mysql update_proxy command:%s' % command)
            self.cursor.execute(command)
        except Exception as e:
            logging.exception('mysql update_proxy exception msg:%s' % e)

    def query(self, command, commit=False):
        try:
            logging.debug('mysql execute command:%s' % command)

            self.cursor.execute(command)
            data = self.cursor.fetchall()
            if commit:
                self.conn.commit()
            return data
        except Exception as e:
            logging.error('mysql execute exception msg:%s' % e)
            return None

    def query_one(self, command, commit=False):
        try:
            logging.debug('mysql execute command:%s' % command)

            self.cursor.execute(command)
            data = self.cursor.fetchone()
            if commit:
                self.conn.commit()

            return data
        except Exception as e:
            logging.debug('mysql execute exception msg:%s' % str(e))
            return None

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
        print('mysql connection close')


if __name__ == '__main__':
    mysql = MySqlRecipes()
    mysql.close()
