'''
Created on 2017年10月27日

@author: dell
'''
import time
import random
import string


class IDGenerator:
    array = []

    @classmethod
    def get_id(cls):
        '''生成主键id（23位），生成规则:17位时间戳（精确到毫秒）+6位随机数。'''
        now = time.strftime("%Y%m%d%H%M%S", time.localtime()) + \
            str(round(time.time(), 3)).split('.')[1].zfill(3)
        random = cls.get_random(6)
        while random in cls.array:
            random = cls.get_random(6)
        current_id = now + random
        cls.array.append(random)
        if len(cls.array) == 1000:
            cls.array.clear()
        return current_id

    @staticmethod
    def get_random(length):
        # 选中numOfNum个数字
        slcNum = [random.choice(string.digits) for i in range(length)]
        random.shuffle(slcNum)
        # 生成密码
        genPwd = ''.join([i for i in slcNum])
        return genPwd


if __name__ == '__main__':
    while True:
        print(IDGenerator.get_id())
