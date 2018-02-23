#!/usr/bin/python
#coding:UTF-8
#coding=UTF-8
"""
-------------------------------------------------
   File Name: wspider.py
   Description: 把比分爬虫搬到这里来，形成数据池
   Author: Dexter Chen
   Date：2017-09-07
-------------------------------------------------
"""

import requests
import sys
import time
from datetime import date, datetime, timedelta
import wconfig
import utilities as ut
import agents
import mongodb_handler as mh
import message as msg
import dictionary as dic