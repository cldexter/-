#!/usr/bin/python
#coding:utf-8
#coding=utf-8
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
from datetime import date, datetime, timedelta
from threading import Timer
import thread

#名词:盘口position,赔率odd,盘口+赔率=offer,offer下单后变成bet
#大小写:公共函数首字母大写,class里面的函数首字母小写,变量首字母小写,公共类首字母大写

# 如下是几个设定,一般不要变
sportId = 1 #足球,其它球类不关心
pageType = 1 #1:今日,2:早盘,3:滚球,4:我的收藏,5:连串过关
programmeId =0 #什么联赛,所有联赛的就留0; 如果有联赛,这个属性将被隐藏,用competitionId代替.现在已知的方法不管联赛
uiBetType = "am"#玩法, am:买大小 fth1X2:胜负平;其它的玩法不管
moreBetEvent = "null" #是否点击了"更多投注"按钮.不点
displayView = 2 #如何显示.已知的办法不用改
pageNo = 0 #第一页, 后续按照1,2,3,4编下去
competitionIds = "" #什么比赛, 每个联赛有个固定的值,26272是澳甲联赛的代号
oddsType = 2 #欧洲盘, 2为香港盘, 3马来盘, 4印尼盘
sortBy = 2 #时间排序, 1为热门排序

#全局变量
startTime = ""#定时开始时间,格式2016-01-12 20:34:45
loopTime = 15 #刷新时间，多少秒,正常情况15秒即可
writeLoop = 10 #多少循环写一次比分记录
rocordBetLoop = 20 #多少次循环写一次bet
maxPorcessTime = 60 # 看门狗容许时间，每次处理程序多少秒，如超过，看门狗中断线程（相当于敲击esc）
secondBetWaitTime = 420 #在盘口回归后, 等待多少秒. 目的是让赔率涨上去一点再买
currentTime = "" #当前时间，非str
endTime = ""#结束时间，非str
timeElapse = "" #流逝的时间，是时间实体，time.timedelta类
runTime = 8 #几个小时后，停止添加新offer实例，不是整个结束。只能手工整个结束。
leagues = [] #服务器抓回来的信息容器
reports = [] #所有报告的容器
recordFile = open('data20160122.txt','a') #文件储存位置
offers = []#所有game的实例都放在这里
bets = []#所有投注都放在这里
allGameBestOffers = []#最后一次更新后的offer,非实例
mode = ""#模式,1是浏览模式,2是自动下注,3是人工干预,4是调试
investment = 0#总投入,考虑了资金回笼的情况
firstBetMoney = 100#首注100, 实际上会更新
secondBetMoney = 100#补注100, 实际上会更新
secondBetMinimalOdd = 1 #盘口回归后, 要等最小什么赔率再补注
balance = "0.00"#有多少钱在账上
globalUpdateCounter = 0#循环了多少次
mimicWaitTime = 5#在模拟过程中,等待多久. 模拟模式5秒,调试模式0秒
familyName = "  "#姓
givenName = "  "#名

#抓取offer的参数,根据模式的不同而变化
earliestAddTime = "00:00" #最早几个提前几个小时将比赛加入关注清单
latestAddTime = "03:00" #已开始多久的比赛不加入关注清单,默认03:00
latestUpdateTime = "85:00" #已开始多久的比赛不再关注（但是不删除）
earliestFirstBetTime = "00:01" #最早第一次下注时刻,00:01表示开踢后，再下注，00:00表示比赛理论上开始就可以下注了
latestFirstBetTime = "04:00" #最迟第一次下注时刻,默认04:00
earlistSecondBetTime = "01:00"#最早补注
latestSecondBetTime = "80:00" #最迟补注,比赛开始后80分钟,再进球就无所谓
# leagueWhiteList = [32149]
leagueWhiteList = [26726,27068,27317,28649,27918,26664,29042,26140,28138,26067,26118,27325,26470,28848,27560,28864,26124,28366,27202,50991,27250]
#白名单包括(顺序对应)：英格兰超级，西班牙甲组，意大利甲组,法国甲组,荷兰甲组,比利时甲组,苏格兰超级,意大利乙组,土耳其超级,葡萄牙超级,希腊超级,英格兰甲组,英格兰乙组,葡萄牙甲组,比利时乙组,苏格兰冠军,土耳其甲组,墨西哥甲组,智利甲组,意大利职业,法国乙组
siteUrls = {"odds":"http://sb-jxf.prdasbbwla1.com/zh-cn/OddsService/GetOdds?","login":"http://www.uedfa.org/zh-cn/member/login.aspx?action=login","add":"http://sb.uedwin.com/zh-cn/BetslipService/Add","bet":"http://sb.uedwin.com/zh-cn/BetslipService/PlaceBet","balance":"http://sb.uedwin.com/zh-cn/UserService/GetBalance?"}#有关这个网站的所有链接
payload = {'ioBB':'','username': 'xuebinhack','password': 'xuebinhack123'}#用于登陆的关键词
headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1', 
			'Host' : 'www.uedfa.me',
			'Connection':'keep-alive',
			'Accept':'*/*',
			'Origin':'http://www.uedfa.me',
			'Referer' : 'http://www.uedfa.me/zh-cn/index.aspx',
			'Accept-Encoding':'gzip, deflate',
			'Accept-Language':'en-US,zh-CN;q=0.8,zh;q=0.6',
			'X-Requested-With':'XMLHttpRequest',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
			}  #所有用于登陆的header

#模式参数,根据模式选择而设定
allowExtendAdd = False#是否准许一直添加,如果选True则忽略最后时间
useLeagueWhiteList = True#是否采用联赛白名单
autoBet = False
autoBetNeedConfirm = False
mimic = False#是否为模拟, 如果是模拟,则不真实投注z
showError = False#是否是调试, 如果是调试,则报错,否则不报错


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

#####################################################################################
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

class Offer:#定义什么是offer, offer=盘口+赔率
	""" 定义offer"""
	def __init__(self,leagueK,leagueName,gameK,hostTeam,awayTeam,gameDate,gameTime,gameHalf,hostTeamScore,awayTeamScore,bigPosition,smallPosition,bigOdds,bigOddsNumber,smallOdds,smallOddsNumber):  															   
		# 一旦生成后不会改变
		self.leagueK = leagueK
		self.leagueName = leagueName
		self.gameK = gameK 
		self.hostTeam = hostTeam 
		self.awayTeam = awayTeam
		self.gameDate = gameDate
		
		# 根据数据流重新赋值
		self.firstBetMoney = firstBetMoney
		self.secondBetMoney = secondBetMoney
		self.gameTime = gameTime
		self.gameHalf = gameHalf
		self.hostTeamScore = hostTeamScore
		self.awayTeamScore = awayTeamScore
		self.bigPosition = bigPosition
		self.smallPosition = smallPosition
		self.bigOdds = bigOdds
		self.bigOddsNumber = bigOddsNumber
		self.bigOddsNumberValue = ""
		self.smallOdds = smallOdds
		self.smallOddsNumber = smallOddsNumber
		self.smallOddsNumberValue = ""
		self.maxSmallPosition = 0
		self.positionTrend = ""
		self.bigOddTrend = ""
		self.smallOddTrend = ""#小赔率变化
		self.betPositionTrend = ""#已买的盘口情况，是否已经出问题
		self.gameStatus = ""#比赛状态
		self.margin = 0 #赚到或者亏掉多少钱，除掉本金后
		self.winLose = "" #“输”或者“赢”
		self.updateCounter = 0 #更新多少次，用于指导写入
		self.readySecondBetCounter = 0#记录在盘口回归后, 有几轮更新
		self.focusBigOddStr = ""
		self.scoresStr = ""
		self.scoreTotal = 0#两边加起来的总分

		# 根据类内规则改变
		self.updateAble = True#是否需要更新
		self.firstBet = False#是否已第一次下注
		self.waitSecondBet = False#是否已需要第二次下注
		self.readySecondBet = False#盘口是否回归,准许第二次下注
		self.secondBet = False#是否已第二次下注

		# 实体内的容器
		self.history = []
		self.historyTemp = []#只用于临时存放，以避免硬盘频繁读写
		self.firstBetRecord = ""#第一次下注详情
		self.firstBetSmallOdd = float(0.0)#第一次下注赔率
		self.firstBetSmallPostion = float(0.0)#第一次下注盘口，数字变量（小）,第二次盘口应该和这个一样
		self.secondBetRecord = ""#第二次下注详情
		self.secondBetBigOdd = float(0.0)#第二次下注赔率
		self.recordFile = open(str(self.gameK)+".txt", "a")
				
	def record(self):
		self.recordStr = self.leagueK,self.leagueName,self.gameK,self.hostTeam,self.awayTeam,self.gameDate,self.gameTime,self.gameHalf,self.hostTeamScore,self.awayTeamScore,self.bigPosition,self.smallPosition,self.bigOdds,self.smallOdds,self.firstBet,self.secondBet
		
		if self.gameStatus == u"[上]" or self.gameStatus == u"[下]": #只有上下场才会写入，中场不理
			self.history.append(self.recordStr)#记录在本实例
			self.historyTemp.append(self.recordStr)#记录在内存临时文件中,以待写入

		if self.updateCounter < writeLoop: # 每隔指定的次数写一次历史到硬盘
			self.updateCounter = self.updateCounter + 1
		else:
			self.recordFile.write(str(self.historyTemp))
			self.historyTemp = []
			self.reportStr = u"  ●存 %s:%s"%(self.hostTeam,self.awayTeam)
			reports.append(self.reportStr)
			self.updateCounter = 0

		self.maxSmallPosition = max([record[11] for record in self.history])#历史上最大的盘口, 放到record里面更新

	def update(self, allGameBestOffers):
		for allGameBestOffer in allGameBestOffers:#遍历所有offer
			if self.gameK == allGameBestOffer[2]:#如果确认本比赛有更新
				if allGameBestOffer[6] != "": #有时间信息就更新，不管有没有历史记录
					self.gameTime = allGameBestOffer[6]
				elif allGameBestOffer[6] == "" and (self.history[-1][6] == "" or self.history[-1][6] == "00:00"):#没有时间信息，也没有历史,或者历史上也是00:00，说明刚开盘 
					self.gameTime = "00:00" #时间不是特别重要
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

				self.smallOddsNumberValue = self.smallOddsNumber[1:]#小盘口编号除去字母部分
				self.bigOddsNumberValue = self.bigOddsNumber[1:]#大盘口编号除去字母部分
				self.scoresStr = str(self.hostTeamScore + ":" + self.awayTeamScore)#

				
				if allGameBestOffer[6] == "" and len(self.history) > 1 and self.history[-1][6] > "44:00" and allGameBestOffer[7] =="HT":#没有时间信息，有历史记录，是中场
					self.gameStatus = u"[中]"
				elif len(self.history) > 1 and self.gameTime >= latestUpdateTime:#没有时间信息，最后一次大于制定时间，是完毕
					self.gameStatus = u"[终]"
				elif (allGameBestOffer[6] == "" or self.gameTime == "00:00") and allGameBestOffer[7] =="":#有时间信息，是00
					self.gameStatus = u"[等]"
				elif self.gameHalf == "1H":
					self.gameStatus = u"[上]"#上半场
				elif self.gameHalf == "2H":
					self.gameStatus = u"[下]"#下半场
				elif len(self.history) > 1 and allGameBestOffer[6] == self.history[-1][6] and self.history[-1][6] > "00:00":
					self.gameStatus = u"[停]"
				elif self.gameHalf == "ET":
					self.gameStatus = "[加]"
				elif self.gameHalf == "Pens":
					self.gameStatus == "[点]"
				else:
					self.gameStatus == "[  ]"

	def status(self):#定义各种符号；根据变化更改状态变量

		self.updateAble = cmp(latestUpdateTime,self.gameTime) == 1 #如果没到最后可更新时间，就继续更新

		if len(self.history)>2:#刚开始的时候没有历史记录，不显示
			if self.smallPosition != "" and self.history[-2][11] != "":		
				if self.smallPosition == self.history[-2][11]:
					self.positionTrend = "→"
				elif self.smallPosition > self.history[-2][11]:
					self.positionTrend = "↑"
				else:
					self.positionTrend = "↓"
			else:
				self.positionTrend = "? "
			if self.smallOdds != "0.00" and self.history[-2][13] != "0.00":
				if self.smallOdds == self.history[-2][13]:
					self.smallOddTrend = "→"
				elif self.smallOdds > self.history[-2][13]:
					self.smallOddTrend = "↑"
				else:
					self.smallOddTrend = "↓"	
			else:
				self.smallOddTrend = "? "

			if self.bigOdds != "0.00" and self.history[-2][12] != "0.00":
				if self.bigOdds == self.history[-2][12]:
					self.bigOddTrend = "→"
				elif self.bigOdds > self.history[-2][12]:
					self.bigOddTrend = "↑"
				else:
					self.bigOddTrend = "↓"	
			else:
				self.bigOddTrend = "? "
		else:
			self.positionTrend = "→"
			self.smallOddTrend = "→"
			self.bigOddTrend = "→"

		if self.firstBet == True:
			self.firstBetStr = u"[首]"
		else:
			self.firstBetStr = u"[  ]"

		if self.secondBet == True:
			self.secondBetStr = u"[补]"
		else:
			self.secondBetStr = u"[  ]"

		if self.firstBetRecord != "": #首注后，把盘口转化为浮点，好和后面进球的整数比较
			self.firstBetSmallPostion = float(self.firstBetRecord[11])
		else:
			self.firstBetSmallPostion = float(0.0)

		if self.firstBetSmallPostion > 0 and float(self.maxSmallPosition) != self.firstBetSmallPostion:#盘口没有比买的时候更大
			self.betPositionTrend = " ?"
			self.waitSecondBet = True
		else:
			self.betPositionTrend = "√"

		if self.waitSecondBet:#盘口曾经高过
			if self.smallPosition == self.firstBetRecord[11]:#盘口又回归了
				self.readySecondBetCounter = self.readySecondBetCounter + 1

		if self.readySecondBetCounter > (secondBetWaitTime/loopTime - 1):
			self.readySecondBet = True


	def display(self):
		self.printColor = COLOR.WHITE
		if self.winLose == u"[赢]" and self.betPositionTrend == "√":
			self.printColor = COLOR.GREEN
		elif self.winLose == u"[输]":
			self.printColor = COLOR.PINK
		elif self.winLose == u"[赢]" and self.betPositionTrend == "??":#有可能输
			self.printColor = COLOR.YELLOW
		else:
			self.printColor = COLOR.WHITE
			
		cPrint(u" │ %s%s%s %s │  %s:%s │ 买 %s%s │  盘 %s%s│ 高 %s │ 大 %s%s│ 小 %s%s│ %s %s │ %s:%s "%(self.firstBetStr,self.secondBetStr,self.winLose,str(self.margin).rjust(5),self.hostTeamScore,self.awayTeamScore,str(self.firstBetSmallPostion).rjust(3),self.betPositionTrend,self.smallPosition.rjust(3),self.positionTrend,self.maxSmallPosition.rjust(3),self.bigOdds,self.bigOddTrend,self.smallOdds,self.smallOddTrend,self.gameTime,self.gameStatus,self.hostTeam,self.awayTeam),self.printColor) 
		
	def firstBetAction(self):# 下注
		if self.firstBet == False: #还没有投注
			self.firstBetCondition1 = self.gameTime > earliestFirstBetTime #在开赛后的某个时间
			self.firstBetCondition2 = self.gameTime < latestFirstBetTime
			self.firstBetCondition3 = self.maxSmallPosition == self.smallPosition #防止盘口曾经到过更高
			self.firstBetCondition4 = len(self.history) > 1 #需要先有至少2个记录，再下注，为了保证条件3是真实的
			self.firstBetCondition5 = balance > firstBetMoney + secondBetMoney#确保只是剩余的钱能够支付首注和补注
			if self.firstBetCondition1 and self.firstBetCondition2 and self.firstBetCondition3 and self.firstBetCondition4 and self.firstBetCondition5:#正在下单操作写在这里	
				if autoBet:
					print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
					with requests.Session() as s:
						loginInformation = s.post(siteUrls['login'], data=payload).json()#先登陆
						print (u" ┌──────┬──────┐\n │ 登陆: %s%s │ %s │\n └──────┴──────┘")%(str(loginInformation['l']['gn']),str(loginInformation['l']['ln']),str(loginInformation['l']['ab']).ljust(10))#显示登陆后的信息,正常情况显示姓名/剩余金额
						self.addSmallOddStr = "{\"ep\":[{\"slid\":%s,\"eid\":%s,\"o\":\"%s\",\"hp\":\"%s\",\"s\":\"%s\",\"isi\":true}],\"sa\":[],\"is\":true}"%(self.smallOddsNumberValue,self.gameK,self.smallOdds,self.smallPosition,self.scoresStr)#生成add指令
						self.firstBetAddInformation = s.post(siteUrls['add'], data=self.addSmallOddStr).json()
						if 'bs' in self.firstBetAddInformation.keys():#确认返还的是json信息
							self.smallPosition = self.firstBetAddInformation['ss'][0]["hp"]#根据add数据,更新盘口(add里面往往是最新的)
							self.smallOdds = self.firstBetAddInformation['ss'][0]["o"]
							print u"  ●添加正确"
							print self.firstBetAddInformation
						i = 0
						for i in range(1):#直接投注3次,成功即跳出,否则则继续
							self.betSmallOddStr = "{\"ep\":[{\"slid\":%s,\"eid\":%s,\"o\":\"%s\",\"hp\":\"%s\",\"s\":\"%s\",\"isi\":true}],\"sa\":[%s],\"is\":true}"%(self.smallOddsNumberValue,self.gameK,self.smallOdds,self.smallPosition,self.scoresStr,self.firstBetMoney)#生成投注指令
							self.firstBetInformation = s.post(siteUrls['bet'], data=self.betSmallOddStr,).json()#投注,并返回数据
							if 'bs' in self.firstBetInformation.keys():#确认返还的是json信息
								if self.firstBetInformation['bs'][0]["wn"] == 0:#如果回复的是没有订单号,就是失败,显示
									print u"  ●正在尝试第%次下注"%i
									self.smallPosition = self.firstBetInformation['ss'][0]["hp"]#根据add数据,更新盘口(add里面往往是最新的)
									self.smallOdds = self.firstBetInformation['ss'][0]["o"]
								else:
									print u"  ●下注成功,下注号为:%s"%self.firstBetInformation['bs'][0]["wn"]
									self.firstBet = True
									self.firstBetRecord = self.leagueK,self.leagueName,self.gameK,self.hostTeam,self.awayTeam,self.gameDate,self.gameTime,self.gameHalf,self.hostTeamScore,self.awayTeamScore,self.bigPosition,self.smallPosition,self.bigOdds,self.smallOdds,self.firstBet,self.secondBet
									bets.append(self.firstBetRecord)
									break
							else:
								print u"  ●下单信息错误"
							i = i + 1
					print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"
				elif mimic:
					print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
					print u"  ●模拟首注中..."
					self.firstBetRecord = self.leagueK,self.leagueName,self.gameK,self.hostTeam,self.awayTeam,self.gameDate,self.gameTime,self.gameHalf,self.hostTeamScore,self.awayTeamScore,self.bigPosition,self.smallPosition,self.bigOdds,self.smallOdds,self.firstBet,self.secondBet
					bets.append(self.firstBetRecord)
					self.firstBet = True			
					time.sleep(mimicWaitTime)
					print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"
			

	def secondBetAction(self):#第二次下注
		if self.firstBet == True: #已经投注过
			self.secondBetCondition1 = self.secondBet == False #还没有补注
			self.secondBetCondition2 = self.gameTime > earlistSecondBetTime#时间合适
			self.secondBetCondition3 = self.gameTime < latestSecondBetTime
			self.secondBetCondition4 = self.maxSmallPosition > self.firstBetRecord[11]#如历史上最大盘口比现在大，说明首注失败，执行补注
			self.secondBetCondition5 = self.readySecondBet #符合最少等待时间
			self.secondBetCondition6 = self.bigOdds > secondBetMinimalOdd#盘口直接大于预设(默认1), 注意, 5/6两个条件选一个即可.
			if self.secondBetCondition1 and self.secondBetCondition2 and self.secondBetCondition3 and self.secondBetCondition4 and (self.secondBetCondition5 or self.secondBetCondition6):
				if autoBet:
					print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
					with requests.Session() as s:
						loginInformation = s.post(siteUrls['login'], data=payload).json()#先登陆
						print (u" ┌──────┬──────┐\n │ 登陆: %s%s │ %s │\n └──────┴──────┘")%(str(loginInformation['l']['gn']),str(loginInformation['l']['ln']),str(loginInformation['l']['ab']).ljust(10))#显示登陆后的信息,正常情况显示姓名/剩余金额
						i = 0
						for i in range(3):#直接投注3次,成功即跳出,否则则继续
							self.betBigOddStr = "{\"ep\":[{\"slid\":%s,\"eid\":%s,\"o\":\"%s\",\"hp\":\"%s\",\"s\":\"%s\",\"isi\":true}],\"sa\":[%s],\"is\":true}"%(self.bigOddsNumberValue,self.gameK,self.bigOdds,self.bigPosition,self.scoresStr,self.secondBetMoney)
							self.secondBetInformation = s.post(siteUrls['bet'], data=self.betBigOddStr).json()#投注,并返回数据
							if 'bs' in self.secondBetInformation.keys():#确认返还的是json信息
								if self.secondBetInformation['bs'][0]["wn"] == "0":#如果回复的是没有订单号,就是失败,显示
									print u"  ●正在尝试第%次下注"%i
									self.bigPosition = self.secondBetInformation['ss'][0]["hp"]#根据add数据,更新盘口(add里面往往是最新的)
									self.bigOdds = self.secondBetInformation['ss'][0]["o"]
								else:
									print u"  ●下注成功,下注号为:%s"%self.secondBetInformation['bs'][0]["wn"]
									self.secondBet = True
									self.secondBetRecord = self.leagueK,self.leagueName,self.gameK,self.hostTeam,self.awayTeam,self.gameDate,self.gameTime,self.gameHalf,self.hostTeamScore,self.awayTeamScore,self.bigPosition,self.smallPosition,self.bigOdds,self.smallOdds,self.firstBet,self.secondBet
									bets.append(self.secondBetRecord)
									break
							else:
								print u"  ●下单信息错误"
							i = i + 1
					print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"
				elif mimic:
					print u" └──────────┴───┴─────┴─────┴────┴─────┴─────┴──────┴─────────────────────────"
					print u"  ●模拟补注中..."
					self.secondBetRecord = self.leagueK,self.leagueName,self.gameK,self.hostTeam,self.awayTeam,self.gameDate,self.gameTime,self.gameHalf,self.hostTeamScore,self.awayTeamScore,self.bigPosition,self.smallPosition,self.bigOdds,self.smallOdds,self.firstBet,self.secondBet
					self.secondBet = True
					bets.append(self.secondBetRecord)
					time.sleep(mimicWaitTime)
					print u" ┌──────────┬───┬─────┬─────┬────┬─────┬─────┬──────┬─────────────────────────"

	def marginCalc(self):
		self.scoreTotal = float(self.hostTeamScore) + float(self.awayTeamScore)
		if self.firstBet == True: #已首注
			if self.secondBet == False: #未补注
				if self.scoreTotal < self.firstBetSmallPostion:#进球小于盘口：赢了
					self.margin = self.firstBetMoney * float(self.firstBetRecord[13])#第一次买小的钱乘以第一次小的赔率
				elif self.scoreTotal > self.firstBetSmallPostion:#未补注，进球大于盘口
					self.margin = 0 - self.firstBetMoney#第一次买小的钱丢了
				else:
					self.margin = 0		
			if self.secondBet == True: #已补注，注意所有输赢判断以第一次买进的计算
				if self.scoreTotal < self.firstBetSmallPostion:#进球小于盘口，赚小不赚大
					self.margin = self.firstBetMoney * float(self.firstBetRecord[13]) - self.secondBetMoney#第一次买小的钱乘以第一次小的赔率，第二次钱丢了
				elif self.scoreTotal > self.firstBetSmallPostion:#进球大于盘口，赚大不赚小
					self.margin = self.secondBetMoney * float(self.secondBetRecord[12]) - self.firstBetMoney#第二次买大的钱乘以第二次买大的赔率, 第一次钱丢了
				else:#如果是平局，就走水，不管有没有补注都利润为零
					self.margin = 0
		else:
			self.margin = 0 #第一次都没买，肯定没钱
		
		if self.margin > 0:
			self.winLose = u"[赢]"
		if self.margin < 0:
			self.winLose = u"[输]"
		if self.margin == 0:
			self.winLose = u"[平]"

class COLOR: #打印颜色的定义，在这里做字典用
    BLACK = 0  
    BLUE = 1  
    DARKGREEN = 2  
    DARKCYAN = 3  
    DARKRED = 4  
    DARKPINK = 5  
    BROWN = 6  
    SILVER = 7  
    GRAY = 8  
    BLUE = 9  
    GREEN = 10  
    CYAN = 11  
    RED = 12  
    PINK = 13  
    YELLOW = 14  
    WHITE = 15

########################################函数部分开始#############################################
def cPrint(msg,color): #实现彩色打印
	import ctypes  
	ctypes.windll.Kernel32.GetStdHandle.restype = ctypes.c_ulong  
	h = ctypes.windll.Kernel32.GetStdHandle(ctypes.c_ulong(0xfffffff5))  
	if isinstance(color, int) == False or color < 0 or color > 15:  
		color = COLOR.SILVER #  
	ctypes.windll.Kernel32.SetConsoleTextAttribute(h, color)  
	print msg
	ctypes.windll.Kernel32.SetConsoleTextAttribute(h, COLOR.SILVER) 

def Request():#发送数据更新请求,更新后的数据存在全局变量中 
	"""从服务器获取的信息"""
	link = siteUrls['odds'] #选择哪个站点,吉祥坊和UED用的一套数据
	timeStamp = str(int(time.time() * 1000))
	isFirstLoad = "true" #是否第一次读取? 需要第一次读取后,获得球队名称等信息
	isInplay = "true" #标记两种数据更新请求: ture,只请求更新inplay区域的; false,更新整页
	payload = {"_":timeStamp,"moreBetEvent":moreBetEvent,"isFirstLoad":"true","uiBetType":uiBetType,"programmeId":programmeId,"pageType":pageType,"sportId":sportId}
	response = requests.get(link,payload).json()#抓回来的是解码json生成的dict文件
	iotLeagues = []#滚球dict,response的子集
	notLeagues = []#今日dict,response的子集
	global leagues
	if 'egs' in response['i-ot'].keys():
		iotLeagues = response['i-ot']['egs'] #"滚球"里面的联赛
	# leagues = iotLeagues
	if 'egs' in response['n-ot'].keys(): #现阶段只考虑已开始的比赛
		notLeagues = response['n-ot']['egs']
	leagues = iotLeagues + notLeagues

def Process():#处理数据,很多层,小心每一层到底是list还是dict,dict就用['es'],list就一定搞遍历(for)
# 以下筛选可以关注的offer,目的是把所有可以投注的offer筛出来，然后让每个offer实体各自去更新
# 筛选offer交给函数，买不买交给对象

# 整体开始
	global allGameBestOffers#先把全局变量清空了
	allGameBestOffers = []
# 选择联赛开始
	for league in leagues: #对每一联赛,进行如下操作
		leagueK = league['c']['k']#联赛编号
		leagueName = league['c']['n']#联赛名字	
		leagueCondition1 = not(u"特别" in leagueName) #不要特别投注,ascii代码:"特别"
		leagueCondition2 = not(u"分钟" in leagueName) #不要非终场的,ascii代码:"分钟"
		if useLeagueWhiteList:
			leagueCondition3 = leagueK in leagueWhiteList #必须是在联赛白名单内的
		else:
			leagueCondition3 = True
		if leagueCondition1 and leagueCondition2 and leagueCondition3:
# 选择比赛开始		
			for game in league['es']: #对每一场比赛,进行如下操作
				thisGameSmallOffers = []#本场比赛所有smalloffers合集, 用于存放该轮选好的offer,最后排序后添加到大offer里面
				gameK = game['k']#比赛编号
				hostTeam = game['i'][0]#主队名字,i/0
				awayTeam = game['i'][1]#客队名称,i/1
				gameDate = game['i'][4]#比赛日期,格式 日/月
				gameTime = game['i'][5]#现在进行到多少时间,如果还没有开始就显示什么时候开始
				hostTeamScore = game['i'][10] #主队得分情况
				awayTeamScore = game['i'][11] #客队得分情况
				gameHalf = game['i'][12] #上下半场,中场TH,用于判断比赛是否开始		
				if 'ou' in game['o'].keys(): #如果有买大小的盘口的话
					offerNumber = len(game['o']['ou'])/8#到底有多少组offer
					gameCondition1 = gameHalf != "ET"#不能是加时赛的
					gameCondition2 = gameHalf != "Pens"#不能买点球的
					gameCondition3 = gameHalf != ""#必须是已开局的比赛
					if gameCondition1 and gameCondition2 and gameCondition3:
# 选offer开始	
						i = 0
						for item in range(0,offerNumber):#生成多个bet offer	
							bigPosition = game['o']['ou'][i*8 + 1]#买大盘口[1]
							smallPosition = game['o']['ou'][i*8 + 3]#买小盘口[3] 和主队盘口应该完全一样
							bigOddsNumber = game['o']['ou'][i*8 + 4]#买大赔率编号[4]
							bigOdds = game['o']['ou'][i*8 + 5]#买大赔率[5]
							smallOddsNumber = game['o']['ou'][i*8 + 6]#买小赔率编号[6]
							smallOdds = game['o']['ou'][i*8 + 7]#买小赔率[7]

							offerCondition1 = not("/" in smallPosition) #盘口不能是双下注
							offerCondition2 = smallOdds > 0 #确保有赔率
							offerCondition3 = smallPosition > 0 #确保有盘口
							if offerCondition1 and offerCondition2 and offerCondition3:
# 这些是可以关注的							
								smallOffer = leagueK,leagueName,gameK,hostTeam,awayTeam,gameDate,gameTime,gameHalf,hostTeamScore,awayTeamScore,bigPosition,smallPosition,bigOdds,smallOdds,bigOddsNumber,smallOddsNumber	
								thisGameSmallOffers.append(smallOffer)
							i = i + 1

				if thisGameSmallOffers:#如果有符合上述条件的offer
					thisGameSmallOffers = sorted(thisGameSmallOffers, key=lambda smallOffer:smallOffer[11],reverse=True)#按照smallposition大小排序
					thisGameBestOffer = thisGameSmallOffers[0]#排序后选第一个
					# thisGameBestPosition = max(thisGameSmallPositions)
					# lowestSmallOdd = thisGameSmallOffers[-1] #暂时用不上,之后可能算法会改
					allGameBestOffers.append(thisGameBestOffer)#把本场比赛最好的offer加到全局储存容器内,这些数据可以用来更新，不全部可以用来创建
									
def addNewGame():#添加新offer实例
	for allGameBestOffer in allGameBestOffers:
		offerAddCondition1 = not(allGameBestOffer[2] in [offer.gameK for offer in offers])#检查在offer容器内是否已经有了
		if allowExtendAdd == False:#如果开了无限加,就忽略最后时间
			offerAddCondition2 = latestAddTime > allGameBestOffer[6] #早于最迟时间
		else:
			offerAddCondition2 = True
		offerAddCondition3 = earliestAddTime < allGameBestOffer[6] #迟于最早时间
		offerAddCondition4 = allGameBestOffer[6] != ""#时间不为空,双保险
		offerAddCondition5 = allGameBestOffer[11] !=""#盘口不能为空,双保险
		offerAddCondition6 = allGameBestOffer[13] !=""#赔率不能为空,双保险
		if offerAddCondition1 and offerAddCondition2 and offerAddCondition3 and offerAddCondition4 and offerAddCondition5 and offerAddCondition6:
			offer = Offer(allGameBestOffer[0],allGameBestOffer[1],allGameBestOffer[2],allGameBestOffer[3],allGameBestOffer[4],allGameBestOffer[5],allGameBestOffer[6],allGameBestOffer[7],allGameBestOffer[8],allGameBestOffer[9],allGameBestOffer[10],allGameBestOffer[11],allGameBestOffer[12],allGameBestOffer[13],allGameBestOffer[14],allGameBestOffer[15]) #实例化offer
			offers.append(offer) #offers是储存offer实例的地方
			reportStr = u"  ●增 %s:%s"% (offer.hostTeam,offer.awayTeam)
			reports.append(reportStr)

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

def Logo():
	cPrint(u"    ■      ■                      ■                    ■                    ■  ■■■■■                ■ ", COLOR.YELLOW)
	cPrint(u"    ■    ■    ■■■            ■  ■            ■■■    ■■■■    ■■■    ■      ■      ■■■■■■■■■■ ", COLOR.YELLOW)
	cPrint(u"    ■  ■■■  ■  ■          ■      ■          ■              ■        ■    ■      ■      ■", COLOR.YELLOW)
	cPrint(u"  ■■■■  ■  ■  ■        ■          ■        ■■■■  ■■■■        ■    ■■■■■      ■  ■■■■■■■", COLOR.YELLOW)
	cPrint(u"    ■  ■■■■    ■■  ■■              ■■    ■              ■    ■■■■                  ■            ■", COLOR.YELLOW)
	cPrint(u"    ■  ■  ■                ■■■■■■          ■■■■■■■■■        ■    ■■■■■      ■    ■■  ■", COLOR.YELLOW)
	cPrint(u"    ■■■■■  ■■■        ■        ■          ■      ■    ■        ■■■      ■          ■        ■", COLOR.YELLOW)
	cPrint(u"  ■■  ■  ■  ■  ■        ■        ■          ■■    ■■  ■        ■■  ■    ■          ■■■■■■■■■■", COLOR.YELLOW)
	cPrint(u"    ■  ■■■  ■  ■        ■        ■          ■      ■    ■      ■  ■    ■■■■■      ■        ■      ■", COLOR.YELLOW)
	cPrint(u"    ■  ■  ■    ■          ■    ■■    ■      ■■    ■■  ■  ■      ■        ■          ■        ■    ■", COLOR.YELLOW)
	cPrint(u"    ■  ■  ■  ■  ■        ■            ■      ■      ■      ■■      ■        ■          ■        ■", COLOR.YELLOW)
	cPrint(u"  ■■■  ■■■      ■        ■■■■■■■      ■■    ■■      ■      ■  ■■■■■■■  ■        ■■              [v0.9]", COLOR.YELLOW)
	print "\n"

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

def Information():
	if len(reports)>0:
		for report in reports:
			print report,
		print "\n"

if __name__ == '__main__':
	RunTask(startTime,loopTime)