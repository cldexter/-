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

from __future__ import division # python除法变来变去的，这句必须放开头
import sys
import time
from datetime import date, datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

reload(sys)
sys.setdefaultencoding('utf8')

# 姓
familyName = "  "  
# 名
givenName = "  "  
# 有多少钱在账上，可以用phantomjs抓取数据更新
balance = "0.00" 

# def Login():#刚刚开始的时候,检查登陆情况
#     global balance,givenName,familyName
#     balanceStr = siteUrls['balance']+"_="+ str(int(time.time() * 1000))
#     balanceLink = siteUrls['login']
#     with requests.Session() as s:
#         cPrint(u"  ●正在登陆中...",COLOR.YELLOW)
#         loginInformation = s.post(balanceLink, data=payload).json()#先登陆
#         cPrint(u" ┌──────┬──────┐\n │ 登陆: %s%s │ %s │\n └──────┴──────┘"%(loginInformation['l']['gn'],loginInformation['l']['ln'],str(loginInformation['l']['ab']).ljust(10)),COLOR.YELLOW)#显示登陆后的信息,正常情况显示姓名/剩余金额
#         balanceStr = loginInformation['l']['ab']
#         balance = balanceStr[4:]
#         givenName = loginInformation['l']['gn']
#         familyName = loginInformation['l']['ln']

class Browser:
    def __init__(self, odds_url, login_url, add_url, bet_url, balance_url, human_url):
        #定义url链接
        self.odds_url = odds_url # 抓数据网址
        self.login_url = login_url # 登陆网址
        self.add_url = add_url # 添加关注网址
        self.bet_url = bet_url # 下单网址
        self.balance_url = balance_url # 获取账号余额网址
        self.human_url = human_url # 人工访问网址
        # 设置浏览器
        self.headers = {
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                         'Referer': "https://www.163.com",
                             "Connection": "keep-alive",
                             "Pragma": "max-age=0",
                             "Cache-Control": "no-cache",
                             "Upgrade-Insecure-Requests": "1",
                             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
                             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                             "Accept-Encoding": "gzip, deflate, sdch",
                             "Accept-Language": "en-US,zh-CN;q=0.8,zh;q=0.6"
                }
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (self.headers)
        dcap["phantomjs.page.settings.loadImages"] = False  # 不载入图片，以加快速度
        # 加载浏览器
        self.browser = webdriver.PhantomJS(
            executable_path='C:\Python27\Scripts\phantomjs.exe', desired_capabilities=dcap)
        self.browser.set_page_load_timeout(60)  # 设定网页加载超时,超过了就不加载
        # 保存浏览器的状态（避免重复加载）
        # "human"
        self.current_url = ""
        self.user_name = "oanzlybc"
        self.user_password = "onlyone"
        self.login = 0 # 刚开始没有登录
        

    def browse(self,url):
        self.current_url = url
        self.browser.get(url)
        print u"  ● 打开 " + self.current_url + " 成功"
        self.browser.save_screenshot("log.png")
        
    def login(self):
        while True:
            # 确保当前
            if self.current_url == self.login_url:
                self.browser.find_element_by_id("loginLink").click()
                self.browser.find_element_by_id("myform:myformloginName").clear()
                self.browser.find_element_by_id("myform:myformloginName").send_keys(self.user_name)
                self.browser.find_element_by_id("myform:myformuserPassword").clear()
                self.browser.find_element_by_id("myform:myformuserPassword").send_keys(self.user_password)
                self.browser.find_element_by_id("myform:j_idt83").send_keys(Keys.ENTER)
                self.browser.save_screenshot("login.png")
                print u"  ● 登陆成功，用户名：" + self.user_name
                break
            else:
                self.browse(self.login_url)
                continue
    
    def balance(self):
        while True:
            # 确保当前连接是对的
            if self.current_url == self.human_url:
                self.browser.find_element_by_class_name('balance flft')
                
            else:
                self.browse(self.balance_url)
                continue


    def close(self):
        self.browser.quit()

if __name__ == '__main__':
    wbrowser = Browser("http://www.wellbet228.net/zh-cn/sportsbook.php","http://www.wellbet228.net/zh-cn/sportsbook.php","http://www.wellbet228.net/zh-cn/sportsbook.php","http://www.wellbet228.net/zh-cn/sportsbook.php","http://www.wellbet228.net/zh-cn/sportsbook.php","http://www.wellbet228.net/zh-cn/sportsbook.php")
    wbrowser.browse("http://www.wellbet228.net/zh-cn/sportsbook.php")
    wbrowser.login()
    wbrowser.close()
