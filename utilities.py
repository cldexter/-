# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: utilities.py
   Description: 所有相关工具
   Author: Dexter Chen
   Date：2017-10-20
-------------------------------------------------
"""

import time

def time_stamp(): # 生成时间戳
    return str(int(time.time() * 1000))


if __name__ == "__main__":
    time_stamp()