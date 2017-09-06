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

def Conclusion():#所有的统计数据都要放到这里
	global reports,investment
	i = 0#正在更新的比赛
	m = 0#完结的比赛
	j = 0#首注
	k = 0#补注
	l = 0#净赚
	n = 0#正在更新的比赛中的首注（用于计算多少实际利用资金）
	o = 0#正在更新中的比赛的补注
	p = 0#用于统计首注即胜的
	for offer in offers:
		if offer.updateAble == True:#多少个正在更新的
			i = i + 1
			if offer.firstBet == True:
				n = n + 1
			if offer.secondBet == True:
				o = o + 1
		if offer.updateAble == False:#多少个过期切完结的
			m = m + 1
		if offer.firstBet == True:#多少个首注
			j = j + 1
		if offer.secondBet == True:#多少个补注
			k = k + 1
		if offer.scoreTotal < offer.firstBetSmallPostion:
			p = p + 1
		l = offer.margin + l #把胜多少钱加一下

	moneyInBet = n*firstBetMoney + o*secondBetMoney#流动资金总数更新
	if moneyInBet > investment:
		investment = moneyInBet

	cPrint(u" ┌─────┬───┬─────┬──────┬──────┬──────┬──────┬──────┐",COLOR.YELLOW) 
	cPrint(u" │ %s │ %s%s │ RMB%s │ 计划 %shr │ 运行 %shr │ 自动 %s │ 确认 %s │ 白名单%s│"%(currentTime.strftime('%H:%M:%S'),givenName,familyName,str(balance).rjust(5),str(runTime).rjust(3),str(timeElapse.seconds/3600).rjust(3),str(autoBet).ljust(5),str(autoBetNeedConfirm).ljust(5),str(useLeagueWhiteList).ljust(5)),COLOR.YELLOW)
	cPrint(u" ├─────┴─┬─┴──┬──┴─┬────┼────┬─┴──┬───┴─┬────┴┬─────┤",COLOR.YELLOW)
	cPrint(u" │ 已跟踪%s比赛 │ %s进行 │ %s完结 │ %s直赢 │ %s首注 │ %s补注 │ 流水%s│ 本金%s│ 纯利%s│"% (str(len(offers)).rjust(2),str(i).rjust(2),str(m).rjust(2),str(p).rjust(2),str(j).rjust(2),str(k).rjust(2),str(len(bets)*firstBetMoney).ljust(5),str(investment).ljust(5),str(int(l)).ljust(5)),COLOR.YELLOW)
	cPrint(u" └───────┴────┴────┴────┴────┴────┴─────┴─────┴─────┘",COLOR.YELLOW)
	reports = [] #清空报告容器