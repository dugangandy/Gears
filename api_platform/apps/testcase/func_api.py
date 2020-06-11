# coding:utf-8
import datetime
import time
from random import choice


def random_warehouse():
    warehouse = ['上海', '无锡', '常州', '苏州', '南京', '杭州', '宁波', '济南']
    return choice(warehouse)


def random_origin():
    origin = ['鞍钢', '本钢', '包钢', '承钢', '柳钢', '日照', '沙钢', '首钢', '武钢', '燕钢']
    return choice(origin)


def random_material():
    material = ['SPHE', 'SPHC']
    return choice(material)


def random_category():
    category = ['C料', '低合金卷', '花纹卷', '普卷', '普碳带钢', '船卷', '冷轧卷', '有花镀锌卷',
                '无花镀锌卷', '冷轧盒板', '酸洗卷', '镀铝锌']
    return choice(category)


def random_specification():
    specification = ['1.8*1250*C', '2.5*1250*C', '2.75*1250*C', '3.0*1250*C']
    return choice(specification)


def random_name():
    name_f = ["张", "王", "李", "赵", "宋", "万", "戴"]
    name_s = ["一一", "一二", "一三", "一四", "一五", "一六", "一七", "一八", "一九"]
    return "{0}{1}".format(choice(name_f), choice(name_s))


def random_mobile():
    mobile_f = ['130', '131', '132', '133', '135', '136', '138', '150', '151']
    num = '0123456789'
    mobile = ''
    for i in range(8): mobile += mobile.join(choice(num))
    return "{0}{1}".format(choice(mobile_f), mobile)


def get_date(days=0):
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=days)
    n_day = now + delta
    return n_day.strftime("%Y-%m-%d")


def get_timestamp():
    return int(round(time.time() * 1000))


if __name__ == '__main__':
    print get_timestamp()
