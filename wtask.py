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

# 运行模式参数,根据模式选择而设定
# 是否准许一直添加,如果选True则忽略最后时间
allowExtendAdd = False
# 是否采用联赛白名单
useLeagueWhiteList = True
# 是否准许自动下单
autoBet = False
# 自动下单前是否需要人工确认
autoBetNeedConfirm = False
# 是否为模拟, 如果是模拟,则不真实下单（模拟等待）
mimic = False
# 是否是调试, 如果是调试,则报错,否则不报错
showError = False

def RunTask(startTime,loopTime):#多少时间后开始运行
	Logo()
	Configuration()
	if mode == "2" and mode == "3":#如果是模式1,4, 就不用登陆了z
		Login()
	global currentTime,endTime,timeElapse#结束时间是全局的
	currentTime = datetime.now()#刷新一下时间
	nowTime = datetime.now()#获取现在的时间
	strNowTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')#现在的时间字符串
	cPrint(u" ┌───────────────┐",COLOR.YELLOW)
	cPrint(u" │ 现在时间: %s│"%strNowTime,COLOR.YELLOW)
	period = timedelta(seconds=loopTime)#定义循环间隔
	if startTime == "":#开始时间
		strStartTime = strNowTime
	else:
		strStartTime = startTime
	cPrint(u" │ 开始时间: %s│"%strStartTime,COLOR.YELLOW)
	runPeriod = timedelta(hours=runTime)
	endTime = currentTime + runPeriod
	cPrint(u" │ 停止新增: %s│"%endTime.strftime('%Y-%m-%d %H:%M:%S'),COLOR.YELLOW)
	cPrint(u" └───────────────┘",COLOR.YELLOW)
	niuniu = Watchdog()#生成看门狗
	while True:#开始循环
		currentTime = datetime.now()
		strCurrentTime = currentTime.strftime('%Y-%m-%d %H:%M:%S')
		timeElapse = currentTime - nowTime
		if str(strCurrentTime) > str(strStartTime):#只要超过，就运行，不等于，因为往往运行滞后。此步骤增强稳定性
			niuniu.StartWatchdog()#开始看门狗
			Tasks()
			nextTime = currentTime + period
			strStartTime = nextTime.strftime('%Y-%m-%d %H:%M:%S')
			niuniu.StopWatchdog()#喂看门狗
			continue

def Tasks():#所有需要循环的任务都列在这里.
	if showError:
		Request() # 收信息
		Process() # 处理信息
		Conclusion()#报告
		if currentTime.strftime('%Y-%m-%d %H:%M:%S') < endTime.strftime('%Y-%m-%d %H:%M:%S'):#如果已经过了增加新实体的时间，即不再增加，旧有的继续更新直到完成
			addNewGame() #根据处理结果产生新offer实体
			# reports.append(u" ●调 时间控制正常")
		if len(offers) != 0:	
			print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"
			for offer in offers:
				if offer.updateAble:#检查实体是否还需更新，超出时间即不用更新了
					offer.update(allGameBestOffers)
					offer.record()#更新实体
				offer.firstBetAction()#尝试首注
				offer.secondBetAction()#尝试补注
				offer.status()#更新符号
				offer.marginCalc()#不管有没有更新，都要刷新钱数
				offer.display()#显示	

			print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
			Information()
	else:
		try:
			Request() # 收信息
			Process() # 处理信息
			Conclusion()#报告
			if currentTime.strftime('%Y-%m-%d %H:%M:%S') < endTime.strftime('%Y-%m-%d %H:%M:%S'):#如果已经过了增加新实体的时间，即不再增加，旧有的继续更新直到完成
				addNewGame() #根据处理结果产生新offer实体
				# reports.append(u" ●调 时间控制正常")
			if len(offers) != 0:	
				print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"
				for offer in offers:
					if offer.updateAble:#检查实体是否还需更新，超出时间即不用更新了
						offer.update(allGameBestOffers)
						offer.record()#更新实体
					offer.firstBetAction()#尝试首注
					offer.secondBetAction()#尝试补注
					offer.status()#更新符号
					offer.marginCalc()#不管有没有更新，都要刷新钱数
					try:
						offer.display()#显示	
					except:
						pass
				print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
				Information()
		except: 
			info=sys.exc_info() 
			print info[0],":",info[1]

class Watchdog(): #看门狗程序，防止运行卡死 
    def __init__(self):
        ''' Class constructor. The "time" argument has the units of seconds. '''
        self._time = maxPorcessTime
        return   
    def StartWatchdog(self):
        ''' Starts the watchdog timer. '''
        self._timer = Timer(self._time, self._WatchdogEvent)
        self._timer.daemon = True
        self._timer.start()
        return    
    def PetWatchdog(self):
        ''' Reset watchdog timer. '''
        self.StopWatchdog()
        self.StartWatchdog()
        return    
    def _WatchdogEvent(self):
        cPrint(u'\n ●调 等待太久，程序强制跳过 \n',COLOR.RED) 
        self.StopWatchdog()
        thread.interrupt_main()
        return
    def StopWatchdog(self):
        ''' Stops the watchdog timer. '''
        self._timer.cancel()

def Configuration():
	#模拟
	cPrint(u" ┌───────┬────┬────┬────┬────┬─────┐\n │ 选择运行模式 │ 1:模拟 │ 2:自动 │ 3:手动 │ 4:调试 │ 回车确认 │\n └───────┴────┴────┴────┴────┴─────┘",COLOR.YELLOW)
	global writeLoop,mode,autoBet,autoBetNeedConfirm,firstBetMoney,secondBetMoney,runTime,mimic,showError,earliestAddTime,latestAddTime,latestUpdateTime,earliestFirstBetTime,latestFirstBetTime,earlistSecondBetTime,latestSecondBetTime,useLeagueWhiteList,mimicWaitTime,secondBetWaitTime
	mode = raw_input(u'  >>> ')
	while True:
		if mode == "1":#浏览模式:和自动一样,只是不真正下单,用于检验程序的可行性
			mimic = True
			break
		elif mode == "2":#自动完成判断和下单
			autoBet = True
			autoBetNeedConfirm = True
			break
		elif mode == "3":#自动完成判断,下单前要确认,回车才下
			autoBet = True
			break
		elif mode == "4":#最大准许条件,让程序试错
			showError = True
			mimic = True
			loopTime = 10#把刷新时间加快
			writeLoop = 3#把记录所需循环数减少
			useLeagueWhiteList = False #不使用白名单
			mimicWaitTime = 0#下单不等待
			secondBetWaitTime = 40
			earliestAddTime = "00:00" #最早加入
			latestAddTime = "80:00" #最迟加入
			latestUpdateTime = "85:00" #最迟更新
			earliestFirstBetTime = "00:00" #最早首注
			latestFirstBetTime = "85:00" #最迟首注
			earlistSecondBetTime = "00:00"#最早补注
			latestSecondBetTime = "85:00" #最迟补注
			break
		else:
			print u"  ●非有效命令, 请重试"
			mode = raw_input(u'  >>> ')
			continue

	cPrint(u" ┌────┬───────┬─────┐\n │ 设定:1 │ 输入首注金额 │ 回车确认 │\n └────┴───────┴─────┘",COLOR.YELLOW)
	betMoneyInput = raw_input(u'  >>> ')
	while True:
		if int(betMoneyInput)>500:
			print u"  ●金额超过上限(RMB 500), 请重试"
			betMoneyInput = raw_input(u'  >>> ')
			continue
		elif int(betMoneyInput)<10:
			print u"  ●金额低于下限(RMB 10), 请重试"
			betMoneyInput = raw_input(u'  >>> ')
			continue
		else:
			firstBetMoney = int(betMoneyInput)
			break

	cPrint(u" ┌────┬───────┬─────┐\n │ 设定:2 │ 输入补注金额 │ 回车确认 │\n └────┴───────┴─────┘",COLOR.YELLOW)
	betMoneyInput = raw_input(u'  >>> ')
	while True:
		if int(betMoneyInput)>500:
			print u"  ●金额超过上限(RMB 500), 请重试"
			betMoneyInput = raw_input(u'  >>> ')
			continue
		elif int(betMoneyInput)<10:
			print u"  ●金额低于下限(RMB 10), 请重试"
			betMoneyInput = raw_input(u'  >>> ')
			continue
		else:
			secondBetMoney = int(betMoneyInput)
			break
	
	cPrint(u" ┌────┬───────┬─────┐\n │ 设定:3 │ 输入运行小时 │ 回车确认 │\n └────┴───────┴─────┘",COLOR.YELLOW)
	runTimeInput = raw_input(u'  >>> ')
	while True:
		if int(runTimeInput)>24:
			print u"  ●时长超过上限(24 Hr), 请重试"
			runTimeInput = raw_input(u'  >>> ')
			continue
		elif int(runTimeInput)<=0:
			print u"  ●不能短于0小时, 请重试"
			runTimeInput = raw_input(u'  >>> ')
			continue
		else:
			runTime = int(runTimeInput)
			break

def Command():
	global allowExtendAdd,autoBet
	cPrint(u" ┌───────┬────┬────┬────┬────┬─────┐\n │ 输入即时指令 │ 1:开加 │ 3:停加 │ 2:开注 │ 4:停注 │ 回车确认 │\n └───────┴────┴────┴────┴────┴─────┘",COLOR.YELLOW)
	commandStr = raw_input('  >>> ')
	while True:
		if mode == "1":#开加
			allowExtendAdd = True
			break
		elif mode == "2":#停加
			allowExtendAdd = False
			break
		elif mode == "3":#开注
			autoBet = True
			break
		elif mode == "4":#停注
			autoBet = False
			break
		else:
			print u"  ●非有效命令, 请重试"
			commandStr = raw_input(u'  >>> ')
			continue