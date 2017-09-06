# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: watcher.py
   Description: 把比分爬虫搬到这里来
   Author: Dexter Chen
   Date：2017-09-06
-------------------------------------------------
   Development Note：
   1.
-------------------------------------------------
   Change Log:
   2018-09-06: 
-------------------------------------------------
#名词规定: 盘口position, 赔率odd, （盘口+赔率）=offer, offer下单后变成bet
#大小写规定: 公共函数首字母大写,class里面的函数首字母小写,变量首字母小写,公共类首字母大写
"""

import requests
import sys
import time
from datetime import date, datetime, timedelta
from threading import Timer
import thread

reload(sys)
sys.setdefaultencoding('utf8')

# 全局变量，如下设定不要变
# sportId:足球
sportId = 1
# pageType: 1:今日,2:早盘,3:滚球,4:我的收藏,5:连串过关
pageType = 1
# programmeId: 定义联赛,所有联赛的就留0; 如果有联赛,这个属性将被隐藏,用competitionId代替.现在已知的方法不管联赛
programmeId = 0
# uiBetType: 玩法, am:买大小 fth1X2:胜负平;其它的玩法不管
uiBetType = "am"
# moreBetEvent: 是否点击了"更多投注"按钮.不点
moreBetEvent = "null"
# displayView: 如何显示.
displayView = 2
# pageNo: 第一页, 后续按照1,2,3,4编下去
pageNo = 0
# competitionIds:什么比赛, 每个联赛有个固定的值,26272是澳甲联赛的代号
competitionIds = ""
# oddsType: 欧洲盘, 2为香港盘, 3马来盘, 4印尼盘
oddsType = 2
# sortBy: 1为热门排序, 2为时间排序
sortBy = 2

#全局变量，定义全局变量容器
# 定时开始时间,格式2016-01-12 20:34:45
startTime = ""
# 刷新时间，多少秒,正常情况15秒即可
loopTime = 15  
# 多少循环写一次比分记录
writeLoop = 10  
# 多少次循环写一次bet，防止频繁读写硬盘
rocordBetLoop = 20 
# 在盘口回归后, 等待多少秒. 目的是让赔率涨上去一点再买
secondBetWaitTime = 420
# 当前时间，非str
currentTime = ""  
# 结束时间，非str
endTime = "" 
 # 流逝的时间，是时间实体，time.timedelta类
timeElapse = "" 
# 几个小时后，停止添加新offer实例，不是整个结束。只能手工整个结束
runTime = 8 
# 服务器抓回来的信息容器
leagues = []  
# 所有报告的容器，注意：报告不是随时打印在屏幕上的，而是收集在一起打印的
reports = []  
# 文件储存位置
recordFile = open('data20160122.txt', 'a')  
# 所有Offer的实例都放在这里，每个抓取的比赛一个
offers = []  
# 所有投注都放在这里
bets = []  
# 最后一次更新后的offer,非实例
allGameBestOffers = [] 
# 运行模式,1是浏览模式,2是自动下注,3是人工干预,4是调试
mode = ""  
# 总投入,考虑了资金回笼的情况
investment = 0
# 首注100, 实际上会更新
firstBetMoney = 100
# 补注100, 实际上会更新
secondBetMoney = 100  
# 盘口回归后, 要等最小什么赔率再补注
secondBetMinimalOdd = 1  
# 循环了多少次 
globalUpdateCounter = 0  
# 在模拟下单过程中,等待多久. 模拟模式5秒,调试模式0秒
mimicWaitTime = 5  
# 看门狗容许时间，每次处理程序多少秒，如超过，看门狗中断线程并重启
maxPorcessTime = 60  


