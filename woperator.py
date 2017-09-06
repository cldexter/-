# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: woperator.py
   Description: 操作phantomjs浏览器完成一系列工作
   Author: Dexter Chen
   Date：2017-09-06
-------------------------------------------------
   Development Note：
   1.
-------------------------------------------------
   Change Log:
   2018-09-06: 
-------------------------------------------------
"""

import sys
import time
from datetime import date, datetime, timedelta

reload(sys)
sys.setdefaultencoding('utf8')

# 姓
familyName = "  "  
# 名
givenName = "  "  
# 有多少钱在账上，可以用phantomjs抓取数据更新
balance = "0.00" 