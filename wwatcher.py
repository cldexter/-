# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: watcher.py
   Description: 把比分爬虫搬到这里来
   Author: Dexter Chen
   Date：2017-09-06
-------------------------------------------------
"""
#名词规定: 盘口position, 赔率odd, （盘口+赔率）=offer, offer下单后变成bet
#大小写规定: 公共函数首字母大写,class里面的函数首字母小写,变量首字母小写,公共类首字母大写

import requests
import sys
import time
from datetime import date, datetime, timedelta


# 全局变量，定义全局变量容器
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

# 全局变量，定义全局变量容器
# 最早几个提前几个小时将比赛加入关注清单
earliestAddTime = "00:00"
# 已开始多久的比赛不加入关注清单,默认03:00
latestAddTime = "03:00"
# 已开始多久的比赛不再关注（但是不删除）
latestUpdateTime = "85:00"
# 最早第一次下注时刻,00:01表示开踢后，再下注，00:00表示比赛理论上开始就可以下注了
earliestFirstBetTime = "00:01"
# 最迟第一次下注时刻,默认04:00
latestFirstBetTime = "04:00"
# 最早补注
earlistSecondBetTime = "01:00"
# 最迟补注,比赛开始后80分钟,再进球就无所谓
latestSecondBetTime = "80:00"
# 白名单
leagueWhiteList = [
    26726,  # 英格兰超级
    27068,  # 西班牙甲组
    27317,  # 意大利甲组
    28649,  # 法国甲组
    27918,  # 荷兰甲组
    26664,  # 比利时甲组
    29042,  # 苏格兰超级
    26140,  # 意大利乙组
    28138,  # 土耳其超级
    26067,  # 葡萄牙超级
    26118,  # 希腊超级
    27325,  # 英格兰甲组
    26470,  # 英格兰乙组
    28848,  # 葡萄牙甲组
    27560,  # 比利时乙组
    28864,  # 苏格兰冠军
    26124,  # 土耳其甲组
    28366,  # 墨西哥甲组
    27202,  # 智利甲组
    50991,  # 意大利职业
    27250  # 法国乙组
]
# 有关这个网站的所有链接:下单、登入，添加关注，下单，余额


# 添加新offer（也是game，有唯一性）实例
def addNewGame(): 
    # 如下是添加offer必须的几个条件 
    for allGameBestOffer in allGameBestOffers:
        # 条件：检查在offer容器内是否已经有了，有就不能添加
        offerAddCondition1 = not(allGameBestOffer[2] in [offer.gameK for offer in offers])  
        # 如果准许无限加（如测试中），就不受此限制
        if allowExtendAdd == False:
            # 条件：早于规定的最迟可添加时间 (默认为开场3分钟)
            offerAddCondition2 = latestAddTime > allGameBestOffer[6]  
        else:
            offerAddCondition2 = True
        # 条件：迟于最早添加时间（默认为开场即可添加）
        offerAddCondition3 = earliestAddTime < allGameBestOffer[6]
        # 条件：时间不为空,双保险
        offerAddCondition4 = allGameBestOffer[6] != ""  
        # 条件：盘口不能为空,双保险
        offerAddCondition5 = allGameBestOffer[11] != ""  
        # 条件：赔率不能为空,双保险
        offerAddCondition6 = allGameBestOffer[13] != ""  
        # 如果全部符合
        if offerAddCondition1 and offerAddCondition2 and offerAddCondition3 and offerAddCondition4 and offerAddCondition5 and offerAddCondition6:
            # 新建一个offer实例
            offer = Offer(allGameBestOffer[0], allGameBestOffer[1], allGameBestOffer[2], allGameBestOffer[3], allGameBestOffer[4], allGameBestOffer[5], allGameBestOffer[6], allGameBestOffer[7],
                          allGameBestOffer[8], allGameBestOffer[9], allGameBestOffer[10], allGameBestOffer[11], allGameBestOffer[12], allGameBestOffer[13], allGameBestOffer[14], allGameBestOffer[15]) 
            # offers是储存offer实例的地方
            offers.append(offer)  
            reportStr = u"  ● 增 %s : %s" % (offer.hostTeam, offer.awayTeam)
            # 把向报告中心加入报告
            reports.append(reportStr)

# 定义offer：offer=盘口+赔率，offer不断变化，符合特定条件的下单变成bet
class Offer:  
    # 初始化offer
    def __init__(self, leagueK, leagueName, gameK, hostTeam, awayTeam, gameDate, gameTime, gameHalf, hostTeamScore, awayTeamScore, bigPosition, smallPosition, bigOdds, bigOddsNumber, smallOdds, smallOddsNumber):
        # 变量：一旦实例化后不会改变
        self.leagueK = leagueK
        self.leagueName = leagueName
        self.gameK = gameK
        self.hostTeam = hostTeam
        self.awayTeam = awayTeam
        self.gameDate = gameDate
        # 变量：初始化后，根据数据流不断重新赋值
        self.gameTime = gameTime
        self.gameHalf = gameHalf
        self.hostTeamScore = hostTeamScore
        self.awayTeamScore = awayTeamScore
        self.bigPosition = bigPosition
        self.smallPosition = smallPosition
        self.bigOdds = bigOdds
        self.bigOddsNumber = bigOddsNumber
        self.smallOdds = smallOdds
        self.smallOddsNumber = smallOddsNumber 
        self.smallOddsNumberValue = self.smallOddsNumber[1:] # 小盘口编号除去字母部分
        self.bigOddsNumberValue = self.bigOddsNumber[1:]  # 大盘口编号除去字母部分
        
        # 变量：根据数据流的赋值加工、计算所得
        self.maxSmallPosition = 0 # 历史上最大的盘口（用于检测是否已经有盘口超过初始盘口）
        self.positionTrend = "" # 盘口变化趋势（与上一次相比）
        self.bigOddTrend = ""  # 买大赔率变化（与上一次相比）
        self.smallOddTrend = ""  # 买小赔率变化（与上一次相比）
        self.betPositionTrend = ""  # 已买的盘口情况，是否已经被超越
        self.gameStatus = ""  # 比赛是否在进行
        self.winLose = ""  # “输”或者“赢”
        self.margin = 0  # 赚到或者亏掉多少钱，除掉本金后
        self.scoreTotal = 0  # 两边加起来的总分
        self.updateCounter = 0  # 更新多少次，用于指导写入
        self.readySecondBetCounter = 0  # 记录在盘口回归后, 有几轮更新
        self.focusBigOddStr = ""
        self.scoresStr = "" # 显示比分
        self.firstBetRecord = ""  # 第一次下注详情
        self.firstBetSmallOdd = float(0.0)  # 第一次下注赔率
        self.firstBetSmallPostion = float(0.0)  # 第一次下注盘口，数字变量（小）,第二次盘口应该和这个一样
        self.secondBetRecord = ""  # 第二次下注详情
        self.secondBetBigOdd = float(0.0)  # 第二次下注赔率
        self.history = [] # 历史文件缓存，永远在内存里面
        self.historyTemp = []  # 历史文件临时存放，隔一段时间就写入硬盘，有间隔，避免硬盘频繁读写
        # 根据类内规则改变
        self.updateAble = True  # 是否需要更新
        self.firstBet = False  # 是否已第一次下注
        self.waitSecondBet = False  # 是否已需要第二次下注
        self.readySecondBet = False  # 盘口是否回归,准许第二次下注
        self.secondBet = False  # 是否已第二次下注
        self.firstBetMoney = firstBetMoney # 首注、补注的金额，根据全局变量赋值
        self.secondBetMoney = secondBetMoney
        # 记录文件
        self.recordFile = open(str(self.gameK) + ".txt", "a+") # 用比赛k值来给文件命名

    # 有关记录的部分
    def record(self):
        # 生成记录数据条
        self.recordStr = self.leagueK, self.leagueName, self.gameK, self.hostTeam, self.awayTeam, self.gameDate, self.gameTime, self.gameHalf, self.hostTeamScore, self.awayTeamScore, self.bigPosition, self.smallPosition, self.bigOdds, self.smallOdds, self.firstBet, self.secondBet
        # 只有上下场才会写入，中场不理
        if self.gameStatus == u"[上]" or self.gameStatus == u"[下]":  
            # 记录在本实例内存
            self.history.append(self.recordStr)  
            # 记录在临时文件中,以待写入硬盘
            self.historyTemp.append(self.recordStr)  
        # 每隔指定的次数写一次历史到硬盘，用的是append的办法
        if self.updateCounter < writeLoop:  
            self.updateCounter += 1
        else:
            self.recordFile.write(str(self.historyTemp))
            self.historyTemp = [] # 及时清空
            self.reportStr = u"  ● 存 %s : %s" % (self.hostTeam, self.awayTeam) # 生成报告信息
            reports.append(self.reportStr) # 放到全局变量的报告容器中
            self.updateCounter = 0 # 循环录入部分归零
        # 历史上最大的盘口, 根据新history值重新计算
        self.maxSmallPosition = max([record[11] for record in self.history])  

    # 更新显示
    def update(self, allGameBestOffers):
        for allGameBestOffer in allGameBestOffers:  # 遍历所有offer
            # 如果遇到比赛有更新（注意，allGameBestOffers数据池里面抓的）
            if self.gameK == allGameBestOffer[2]: 
                # 有时间信息就更新，不管有没有历史记录
                if allGameBestOffer[6] != "":  
                    self.gameTime = allGameBestOffer[6]
                # 没有时间信息，也没有历史,或者历史上也是00:00，说明刚开盘
                elif allGameBestOffer[6] == "" and (self.history[-1][6] == "" or self.history[-1][6] == "00:00"):
                    self.gameTime = "00:00"  # 时间不是特别重要
                # 有信息才更新，没有就不变
                if allGameBestOffer[7] != "":
                    self.gameHalf = allGameBestOffer[7]
                if allGameBestOffer[8] != "":
                    self.hostTeamScore = allGameBestOffer[8]
                if allGameBestOffer[9] != "":
                    self.awayTeamScore = allGameBestOffer[9]
                if allGameBestOffer[10] != "":
                    self.bigPosition = allGameBestOffer[10]
                if allGameBestOffer[11] != "":
                    self.smallPosition = allGameBestOffer[11]
                if allGameBestOffer[12] > "0":
                    self.bigOdds = allGameBestOffer[12]
                if allGameBestOffer[13] > "0":
                    self.smallOdds = allGameBestOffer[13]
                if allGameBestOffer[14] != "":
                    self.bigOddsNumber = allGameBestOffer[14]
                if allGameBestOffer[15] != "":
                    self.smallOddsNumber = allGameBestOffer[15]
                # 更新一系列信息
                # 更新比分显示
                self.scoresStr = str(self.hostTeamScore +":" + self.awayTeamScore)
                # 没有时间信息，但是有历史记录，是中场
                if allGameBestOffer[6] == "" and len(self.history) > 1 and self.history[-1][6] > "44:00" and allGameBestOffer[7] == "HT":
                    self.gameStatus = u"[中]"
                # 没有时间信息，最后一次大于制定时间，是比赛已结束
                elif len(self.history) > 1 and self.gameTime >= latestUpdateTime:
                    self.gameStatus = u"[终]"
                # 比赛正准备开始
                elif (allGameBestOffer[6] == "" or self.gameTime == "00:00") and allGameBestOffer[7] == "":
                    self.gameStatus = u"[等]"
                # 上半场
                elif self.gameHalf == "1H":
                    self.gameStatus = u"[上]"
                # 下半场
                elif self.gameHalf == "2H":
                    self.gameStatus = u"[下]"
                # 比赛暂停
                elif len(self.history) > 1 and allGameBestOffer[6] == self.history[-1][6] and self.history[-1][6] > "00:00":
                    self.gameStatus = u"[停]"
                # 进入加时赛
                elif self.gameHalf == "ET":
                    self.gameStatus = "[加]"
                # 正在点球
                elif self.gameHalf == "Pens":
                    self.gameStatus == "[点]"
                else:
                    self.gameStatus == "[  ]"
  
        # 如果没到最后可更新时间，就继续更新
        self.updateAble = cmp(latestUpdateTime, self.gameTime) == 1
        # 刚开始的时候没有历史记录，趋势都为"→"
        if len(self.history) > 2:  
            # 已经抓取两次后，开始判断盘口正在趋势
            if self.smallPosition != "" and self.history[-2][11] != "":
                if self.smallPosition == self.history[-2][11]:
                    self.positionTrend = "→"
                elif self.smallPosition > self.history[-2][11]:
                    self.positionTrend = "↑"
                else:
                    self.positionTrend = "↓"
            else:
                self.positionTrend = "? "
            # 买小赔率的变化趋势
            if self.smallOdds != "0.00" and self.history[-2][13] != "0.00":
                if self.smallOdds == self.history[-2][13]:
                    self.smallOddTrend = "→"
                elif self.smallOdds > self.history[-2][13]:
                    self.smallOddTrend = "↑"
                else:
                    self.smallOddTrend = "↓"
            else:
                self.smallOddTrend = "? "
            # 买大赔率的变化趋势
            if self.bigOdds != "0.00" and self.history[-2][12] != "0.00":
                if self.bigOdds == self.history[-2][12]:
                    self.bigOddTrend = "→"
                elif self.bigOdds > self.history[-2][12]:
                    self.bigOddTrend = "↑"
                else:
                    self.bigOddTrend = "↓"
            else:
                self.bigOddTrend = "? "
        # 没有两次历史，暂不判断趋势
        else:
            self.positionTrend = "→"
            self.smallOddTrend = "→"
            self.bigOddTrend = "→"
        # 显示是否已下注
        if self.firstBet == True:
            self.firstBetStr = u"[首]"
        else:
            self.firstBetStr = u"[  ]"
        if self.secondBet == True:
            self.secondBetStr = u"[补]"
        else:
            self.secondBetStr = u"[  ]"
        # 首注后，把盘口转化为浮点，好和后面进球的整数比较
        if self.firstBetRecord != "":  
            self.firstBetSmallPostion = float(self.firstBetRecord[11])
        else:
            self.firstBetSmallPostion = float(0.0)
        # 如果已首注，且最大盘口不等于首注
        if self.firstBetSmallPostion > 0 and float(self.maxSmallPosition) != self.firstBetSmallPostion:
            # 出问题了：需要等待补注
            self.betPositionTrend = " ?"
            self.waitSecondBet = True
        else:
            # 没问题显示√
            self.betPositionTrend = "√"
        # 如果已等待补注
        if self.waitSecondBet:
            # 盘口又回归了
            if self.smallPosition == self.firstBetRecord[11]: 
                # 等待补注的计数器加1 
                self.readySecondBetCounter = self.readySecondBetCounter + 1
        # 当等待补注的时间够了后，补注
        if self.readySecondBetCounter > (secondBetWaitTime / loopTime - 1):
            self.readySecondBet = True

    # 显示全部分离，此处只抛出要显示的内容，不直接打印
    def display(self):
        self.printColor = COLOR.WHITE
        if self.winLose == u"[赢]" and self.betPositionTrend == "√":
            self.printColor = COLOR.GREEN
        elif self.winLose == u"[输]":
            self.printColor = COLOR.PINK
        elif self.winLose == u"[赢]" and self.betPositionTrend == "??":  # 有可能输
            self.printColor = COLOR.YELLOW
        else:
            self.printColor = COLOR.WHITE

        cPrint(u" │ %s%s%s %s │  %s:%s │ 买 %s%s │  盘 %s%s│ 高 %s │ 大 %s%s│ 小 %s%s│ %s %s │ %s:%s " % (self.firstBetStr, self.secondBetStr, self.winLose, str(self.margin).rjust(5), self.hostTeamScore, self.awayTeamScore, str(self.firstBetSmallPostion).rjust(3), self.betPositionTrend, self.smallPosition.rjust(3), self.positionTrend, self.maxSmallPosition.rjust(3), self.bigOdds, self.bigOddTrend, self.smallOdds, self.smallOddTrend, self.gameTime, self.gameStatus, self.hostTeam, self.awayTeam), self.printColor)

    # 现在开始下注相关判断
    def firstBetAction(self): 
        # 还没有首注
        if self.firstBet == False: 
            # 开始条件判断 
            self.firstBetCondition1 = self.gameTime > earliestFirstBetTime  # 迟于最早可以首注时间
            self.firstBetCondition2 = self.gameTime < latestFirstBetTime # 早于最迟可以首注时间
            self.firstBetCondition3 = self.maxSmallPosition == self.smallPosition  # 最大盘口就是现在盘口，防止盘口曾经到过更高
            self.firstBetCondition4 = len(self.history) > 1 # 需要先有至少1个以上记录，再下注，为了保证条件3是真实的
            self.firstBetCondition5 = balance > (firstBetMoney + secondBetMoney)  # 确保账上的钱能够支付首注和补注
            # 如果上述条件都符合：正在下单操作
            if self.firstBetCondition1 and self.firstBetCondition2 and self.firstBetCondition3 and self.firstBetCondition4 and self.firstBetCondition5:  
                if autoBet:
                    print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
                    with requests.Session() as s:
                        loginInformation = s.post(
                            siteUrls['login'], data=payload).json()  # 先登陆
                        print (u" ┌──────┬──────┐\n │ 登陆: %s%s │ %s │\n └──────┴──────┘") % (str(loginInformation['l']['gn']), str(
                            loginInformation['l']['ln']), str(loginInformation['l']['ab']).ljust(10))  # 显示登陆后的信息,正常情况显示姓名/剩余金额
                        self.addSmallOddStr = "{\"ep\":[{\"slid\":%s,\"eid\":%s,\"o\":\"%s\",\"hp\":\"%s\",\"s\":\"%s\",\"isi\":true}],\"sa\":[],\"is\":true}" % (
                            self.smallOddsNumberValue, self.gameK, self.smallOdds, self.smallPosition, self.scoresStr)  # 生成add指令
                        self.firstBetAddInformation = s.post(
                            siteUrls['add'], data=self.addSmallOddStr).json()
                        if 'bs' in self.firstBetAddInformation.keys():  # 确认返还的是json信息
                            # 根据add数据,更新盘口(add里面往往是最新的)
                            self.smallPosition = self.firstBetAddInformation['ss'][0]["hp"]
                            self.smallOdds = self.firstBetAddInformation['ss'][0]["o"]
                            print u"  ●添加正确"
                            print self.firstBetAddInformation
                        i = 0
                        for i in range(1):  # 直接投注3次,成功即跳出,否则则继续
                            self.betSmallOddStr = "{\"ep\":[{\"slid\":%s,\"eid\":%s,\"o\":\"%s\",\"hp\":\"%s\",\"s\":\"%s\",\"isi\":true}],\"sa\":[%s],\"is\":true}" % (
                                self.smallOddsNumberValue, self.gameK, self.smallOdds, self.smallPosition, self.scoresStr, self.firstBetMoney)  # 生成投注指令
                            self.firstBetInformation = s.post(
                                siteUrls['bet'], data=self.betSmallOddStr,).json()  # 投注,并返回数据
                            if 'bs' in self.firstBetInformation.keys():  # 确认返还的是json信息
                                # 如果回复的是没有订单号,就是失败,显示
                                if self.firstBetInformation['bs'][0]["wn"] == 0:
                                    print u"  ●正在尝试第%次下注" % i
                                    # 根据add数据,更新盘口(add里面往往是最新的)
                                    self.smallPosition = self.firstBetInformation['ss'][0]["hp"]
                                    self.smallOdds = self.firstBetInformation['ss'][0]["o"]
                                else:
                                    print u"  ●下注成功,下注号为:%s" % self.firstBetInformation['bs'][0]["wn"]
                                    self.firstBet = True
                                    self.firstBetRecord = self.leagueK, self.leagueName, self.gameK, self.hostTeam, self.awayTeam, self.gameDate, self.gameTime, self.gameHalf, self.hostTeamScore, self.awayTeamScore, self.bigPosition, self.smallPosition, self.bigOdds, self.smallOdds, self.firstBet, self.secondBet
                                    bets.append(self.firstBetRecord)
                                    break
                            else:
                                print u"  ●下单信息错误"
                            i = i + 1
                    print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"
                elif mimic:
                    print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
                    print u"  ●模拟首注中..."
                    self.firstBetRecord = self.leagueK, self.leagueName, self.gameK, self.hostTeam, self.awayTeam, self.gameDate, self.gameTime, self.gameHalf, self.hostTeamScore, self.awayTeamScore, self.bigPosition, self.smallPosition, self.bigOdds, self.smallOdds, self.firstBet, self.secondBet
                    bets.append(self.firstBetRecord)
                    self.firstBet = True
                    time.sleep(mimicWaitTime)
                    print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"

    def secondBetAction(self):  # 第二次下注
        if self.firstBet == True:  # 已经投注过
            self.secondBetCondition1 = self.secondBet == False  # 还没有补注
            self.secondBetCondition2 = self.gameTime > earlistSecondBetTime  # 时间合适
            self.secondBetCondition3 = self.gameTime < latestSecondBetTime
            # 如历史上最大盘口比现在大，说明首注失败，执行补注
            self.secondBetCondition4 = self.maxSmallPosition > self.firstBetRecord[11]
            self.secondBetCondition5 = self.readySecondBet  # 符合最少等待时间
            # 盘口直接大于预设(默认1), 注意, 5/6两个条件选一个即可.
            self.secondBetCondition6 = self.bigOdds > secondBetMinimalOdd
            if self.secondBetCondition1 and self.secondBetCondition2 and self.secondBetCondition3 and self.secondBetCondition4 and (self.secondBetCondition5 or self.secondBetCondition6):
                if autoBet:
                    print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
                    with requests.Session() as s:
                        loginInformation = s.post(
                            siteUrls['login'], data=payload).json()  # 先登陆
                        print (u" ┌──────┬──────┐\n │ 登陆: %s%s │ %s │\n └──────┴──────┘") % (str(loginInformation['l']['gn']), str(
                            loginInformation['l']['ln']), str(loginInformation['l']['ab']).ljust(10))  # 显示登陆后的信息,正常情况显示姓名/剩余金额
                        i = 0
                        for i in range(3):  # 直接投注3次,成功即跳出,否则则继续
                            self.betBigOddStr = "{\"ep\":[{\"slid\":%s,\"eid\":%s,\"o\":\"%s\",\"hp\":\"%s\",\"s\":\"%s\",\"isi\":true}],\"sa\":[%s],\"is\":true}" % (
                                self.bigOddsNumberValue, self.gameK, self.bigOdds, self.bigPosition, self.scoresStr, self.secondBetMoney)
                            self.secondBetInformation = s.post(
                                siteUrls['bet'], data=self.betBigOddStr).json()  # 投注,并返回数据
                            if 'bs' in self.secondBetInformation.keys():  # 确认返还的是json信息
                                # 如果回复的是没有订单号,就是失败,显示
                                if self.secondBetInformation['bs'][0]["wn"] == "0":
                                    print u"  ●正在尝试第%次下注" % i
                                    # 根据add数据,更新盘口(add里面往往是最新的)
                                    self.bigPosition = self.secondBetInformation['ss'][0]["hp"]
                                    self.bigOdds = self.secondBetInformation['ss'][0]["o"]
                                else:
                                    print u"  ●下注成功,下注号为:%s" % self.secondBetInformation['bs'][0]["wn"]
                                    self.secondBet = True
                                    self.secondBetRecord = self.leagueK, self.leagueName, self.gameK, self.hostTeam, self.awayTeam, self.gameDate, self.gameTime, self.gameHalf, self.hostTeamScore, self.awayTeamScore, self.bigPosition, self.smallPosition, self.bigOdds, self.smallOdds, self.firstBet, self.secondBet
                                    bets.append(self.secondBetRecord)
                                    break
                            else:
                                print u"  ●下单信息错误"
                            i = i + 1
                    print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"
                elif mimic:
                    print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
                    print u"  ●模拟补注中..."
                    self.secondBetRecord = self.leagueK, self.leagueName, self.gameK, self.hostTeam, self.awayTeam, self.gameDate, self.gameTime, self.gameHalf, self.hostTeamScore, self.awayTeamScore, self.bigPosition, self.smallPosition, self.bigOdds, self.smallOdds, self.firstBet, self.secondBet
                    self.secondBet = True
                    bets.append(self.secondBetRecord)
                    time.sleep(mimicWaitTime)
                    print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"

    def marginCalc(self):
        self.scoreTotal = float(self.hostTeamScore) + float(self.awayTeamScore)
        if self.firstBet == True:  # 已首注
            if self.secondBet == False:  # 未补注
                if self.scoreTotal < self.firstBetSmallPostion:  # 进球小于盘口：赢了
                    self.margin = self.firstBetMoney * \
                        float(self.firstBetRecord[13])  # 第一次买小的钱乘以第一次小的赔率
                elif self.scoreTotal > self.firstBetSmallPostion:  # 未补注，进球大于盘口
                    self.margin = 0 - self.firstBetMoney  # 第一次买小的钱丢了
                else:
                    self.margin = 0
            if self.secondBet == True:  # 已补注，注意所有输赢判断以第一次买进的计算
                if self.scoreTotal < self.firstBetSmallPostion:  # 进球小于盘口，赚小不赚大
                    self.margin = self.firstBetMoney * \
                        float(
                            self.firstBetRecord[13]) - self.secondBetMoney  # 第一次买小的钱乘以第一次小的赔率，第二次钱丢了
                elif self.scoreTotal > self.firstBetSmallPostion:  # 进球大于盘口，赚大不赚小
                    self.margin = self.secondBetMoney * \
                        float(
                            self.secondBetRecord[12]) - self.firstBetMoney  # 第二次买大的钱乘以第二次买大的赔率, 第一次钱丢了
                else:  # 如果是平局，就走水，不管有没有补注都利润为零
                    self.margin = 0
        else:
            self.margin = 0  # 第一次都没买，肯定没钱

        if self.margin > 0:
            self.winLose = u"[赢]"
        if self.margin < 0:
            self.winLose = u"[输]"
        if self.margin == 0:
            self.winLose = u"[平]"
