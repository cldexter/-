# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: wstats.py
   Description: 统计运行中的参数、总数等
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
from threading import Timer
import thread

reload(sys)
sys.setdefaultencoding('utf8')

