# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: utilities.py
   Description: 多次用到的小工具：时间，文字清理等
   Author: Dexter Chen
   Date：2017-09-14
-------------------------------------------------
"""
import sys
import time
import re
import dictionary
import datetime
import thread
from threading import Timer

# 输出时间，带日期和不带; delta_hr 是往后数多少小时，负数往前数

def time_stamp():
    return str(int(time.time() * 1000))


def time_str(type="full", delta_min=0): # 自然时间的时间戳
    if type == "full":  # 完整时间
        time_format = '%Y-%m-%d %X'
    if type == "time":  # 只有时间
        time_format = "%X"
    if type == "year": # 年份
        time_format = "%Y"
    time_str = datetime.datetime.now()
    time = time_str + datetime.timedelta(minutes=delta_min)
    return time.strftime(time_format)


def time_str_converter(date_str_short, time_str_short): # 把 8/10 这样的时间转为标准的
    month_day = date_str_short.split("/")
    day = month_day[0]
    month = month_day[1]
    year = time_str("year")
    return year + "-" + month + "-" + day + " " + time_str_short + ":00" # 00 是秒，原始的时间总没有
    


def time_object(time_str):
    return time.strptime(time_str, "%Y-%m-%d %X")


def time_str_duration(early_time_str, late_time_str, time_unit="hour"): # 计算两个时间str之间的时间差，默认输出s，也可输出min
    early_time_object = datetime.datetime.strptime(early_time_str, "%Y-%m-%d %X")
    late_time_object = datetime.datetime.strptime(late_time_str, "%Y-%m-%d %X")
    duration_delta = late_time_object - early_time_object
    duration_in_seconds = int(duration_delta.total_seconds())
    if time_unit == "second":
        return duration_in_seconds
    elif time_unit == "minute":
        return duration_in_seconds / 60
    elif time_unit == "hour":
        return duration_in_seconds / 3600
    elif time_unit == "day":
        return duration_in_seconds / 86400
    else:
        return "error"


# 用于根据字典文件替换
def dict_replace(data, re_dict):
    for (k, j) in re_dict.items():
        data = data.replace(k, j)
    return data


# 用正则表达式进行，正则表达式可以不断加
re_html = "</?\w+[^>]*>\s?"  # 清除所有html标签
re_email_general = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


def regexp_replace(data, re_data):
    # 用正则表达式去除标签
    re_content = re.compile(re_data)  # 清除所有html标签
    data = re_content.sub('', data)
    return data


def cur_file_dir():  # 获取脚本路径
    path = sys.path[0]
    return path


if __name__ == '__main__':
    # print time_str_duration("2010-10-10 10:10:10", "2010-10-10 11:10:10")
    # print time_str("full")
    # print time_str("full", 30)
    # print time_str("year")
    print time_str_duration(time_str("full"), time_str_converter("10/10", "12:30"))