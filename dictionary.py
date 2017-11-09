# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: dictionary.py
   Description: 各种字典文件
   Author: Dexter Chen
   Date：2017-09-09
-------------------------------------------------
"""

dict_direction = {
    u"东南": "SE",
    u"西南": "SW",
    u"东北": "NE",
    u"西北": "NW",
    u"南": "S",
    u"北": "N",
    u"西": "W",
    u"东": "E",
    u"未知": "U",
    u"三面单边": "DDD"
}

dict_decoration = {
    u"豪装": "6",
    u"精装": "4",
    u"中装": "3",
    u"简装": "2",
    u"毛坯": "1",
    u"发展商装修": "5",
    u"其他": "0"
}


dict_floor_type = {
    u"高层": "H",
    u"中层": "M",
    u"低层": "L"
}


if __name__ == '__main__':
    print sorted(country_names.keys())