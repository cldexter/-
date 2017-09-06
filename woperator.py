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

def Login():#刚刚开始的时候,检查登陆情况
	global balance,givenName,familyName
	balanceStr = siteUrls['balance']+"_="+ str(int(time.time() * 1000))
	balanceLink = siteUrls['login']
	with requests.Session() as s:
		cPrint(u"  ●正在登陆中...",COLOR.YELLOW)
		loginInformation = s.post(balanceLink, data=payload).json()#先登陆
		cPrint(u" ┌──────┬──────┐\n │ 登陆: %s%s │ %s │\n └──────┴──────┘"%(loginInformation['l']['gn'],loginInformation['l']['ln'],str(loginInformation['l']['ab']).ljust(10)),COLOR.YELLOW)#显示登陆后的信息,正常情况显示姓名/剩余金额
		balanceStr = loginInformation['l']['ab']
		balance = balanceStr[4:]
		givenName = loginInformation['l']['gn']
		familyName = loginInformation['l']['ln']
