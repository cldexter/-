# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: wspider.py
   Description: 把比分爬虫搬到这里来，形成数据池
   Author: Dexter Chen
   Date：2017-09-07
-------------------------------------------------
   Development Note：
   1.
-------------------------------------------------
   Change Log:
   2018-09-06: 
-------------------------------------------------
"""

import requests
import sys
import time
from datetime import date, datetime, timedelta

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

siteUrls = {
    "odds": "http://sb-jxf.prdasbbwla1.com/zh-cn/OddsService/GetOdds?", # 信息页
    "login": "http://www.wellbet228.net/zh-cn/sportsbook.php", # 登录页
    "add": "http://www.wellbet228.net/zh-cn/sportsbook.php", # 添加页
    "bet": "http://www.wellbet228.net/zh-cn/sportsbook.php", # 下注页
    "balance": "http://www.wellbet228.net/zh-cn/uc/user/user_info.php", # 剩余金额
    "human": "http://www.wellbet228.net/zh-cn/sportsbook.php" # 正常浏览
}

# 发送数据更新请求,更新后的数据存在全局变量中
def Request():
    # leagues是抓回来的数据容器
    global leagues
    # 选择哪个站点,吉祥坊和UED用的一套数据
    link = siteUrls['odds']
    # 生成时间戳
    timeStamp = str(int(time.time() * 1000))
    # 是否第一次读取，如果是，强制获得球队名称等信息。未来改为“非第一次”加快速度
    isFirstLoad = "true"
    # 标记两种数据更新请求: ture,只请求更新inplay区域的; false,更新整页
    isInplay = "true"  
    # 定义链接请求参数，已调好，不要动
    payload = {
        "_": timeStamp, 
        "moreBetEvent": moreBetEvent, 
        "isFirstLoad": "true",
        "uiBetType": uiBetType, 
        "programmeId": programmeId, 
        "pageType": pageType, 
        "sportId": sportId
    }
    # 抓回来的是解码json生成的dict文件
    response = requests.get(link, payload).json() 
    # 滚球信息dict,response的子集
    iotLeagues = []  
    # 今日信息dict,response的子集，已开始的比赛
    notLeagues = []
    # 重新合成抓回来的数据
    if 'egs' in response['i-ot'].keys():
        # "滚球"里面的联赛
        iotLeagues = response['i-ot']['egs']  
    if 'egs' in response['n-ot'].keys(): 
        # 现阶段只考虑已开始的比赛 
        notLeagues = response['n-ot']['egs']
    leagues = iotLeagues + notLeagues

# 处理数据,很多层,小心每一层到底是list还是dict,dict就用['es'],list就一定搞遍历(for)
# 以下筛选可以关注的offer,目的是把所有可以投注的offer筛出来，然后让每个offer实体各自去更新
# 筛选offer交给函数，买不买交给对象
def Process():  
    # 整体开始
    global allGameBestOffers 
    # 先把全局变量清空了
    allGameBestOffers = []
    # 选择联赛开始，对每一联赛,进行如下操作
    for league in leagues:  
        leagueK = league['c']['k']  # 联赛编号
        leagueName = league['c']['n']  # 联赛名字
        # 如下是联赛必须符合的几个条件
        leagueCondition1 = not(u"特别" in leagueName)  # 条件：排除特别投注
        leagueCondition2 = not(u"分钟" in leagueName)  # 条件：排除非全场比赛的（如只赌上半场）
        # 条件：如果使用白名单，必须是在联赛白名单内的，否则所有都可
        if useLeagueWhiteList:
            leagueCondition3 = leagueK in leagueWhiteList
        else:
            leagueCondition3 = True
        # 如果全部符合
        if leagueCondition1 and leagueCondition2 and leagueCondition3:
            # 选择比赛开始
            for game in league['es']:  # 对每一场比赛,进行如下操作
                # 本场比赛所有smalloffers合集,用于存放该轮选好的offer,最后排序后添加到大offer里面
                thisGameSmallOffers = []  
                gameK = game['k']  # 比赛编号
                hostTeam = game['i'][0]  # 主队名字
                awayTeam = game['i'][1]  # 客队名称
                gameDate = game['i'][4]  # 比赛日期,格式 日/月
                gameTime = game['i'][5]  # 现在进行到多少时间,如果还没有开始就显示什么时候开始
                hostTeamScore = game['i'][10]  # 主队得分情况
                awayTeamScore = game['i'][11]  # 客队得分情况
                gameHalf = game['i'][12]  # 上下半场,中场TH,用于判断比赛是否开始
                 # 如果有买大小的盘口的话
                if 'ou' in game['o'].keys(): 
                    offerNumber = len(game['o']['ou']) / 8  # 到底有多少组offer
                    # 如下是比赛必须符合的几个条件
                    gameCondition1 = gameHalf != "ET"  # 条件：不能是加时赛的
                    gameCondition2 = gameHalf != "Pens"  # 条件：不能买点球的
                    gameCondition3 = gameHalf != ""  # 条件：必须是已开局的比赛
                    # 如果全部符合
                    if gameCondition1 and gameCondition2 and gameCondition3:
                        # 添加offer开始
                        i = 0
                        for item in range(0, offerNumber):  # 生成多个bet offer
                            # 买大盘口[1]
                            bigPosition = game['o']['ou'][i * 8 + 1]  
                            # 买小盘口[3]和主队盘口应该完全一样
                            smallPosition = game['o']['ou'][i * 8 + 3]
                            # 买大赔率编号[4]
                            bigOddsNumber = game['o']['ou'][i * 8 + 4]
                            # 买大赔率[5]
                            bigOdds = game['o']['ou'][i * 8 + 5]  
                            # 买小赔率编号[6]
                            smallOddsNumber = game['o']['ou'][i * 8 + 6]
                            # 买小赔率[7]
                            smallOdds = game['o']['ou'][i * 8 + 7]  
                            # 如下是offer必须符合的几个条件
                            offerCondition1 = not("/" in smallPosition)  # 条件：盘口不能是双下注（同时下注相邻两个盘口）
                            offerCondition2 = smallOdds > 0  # 条件：确保有赔率
                            offerCondition3 = smallPosition > 0  # 条件：确保有盘口
                            # 如果全部符合
                            if offerCondition1 and offerCondition2 and offerCondition3:
                                # 买小（smallOffer）是我们玩的主要东西
                                smallOffer = leagueK, leagueName, gameK, hostTeam, awayTeam, gameDate, gameTime, gameHalf, hostTeamScore, awayTeamScore, bigPosition, smallPosition, bigOdds, smallOdds, bigOddsNumber, smallOddsNumber
                                # 把这个比赛所有小都凑到一起（一个比赛不止一个smallOffer）
                                thisGameSmallOffers.append(smallOffer)
                            i += 1
                # 如果有符合上述条件的offer
                if thisGameSmallOffers:  
                    # 按照smallposition大小排序，只卖其中最大那个
                    thisGameSmallOffers = sorted(thisGameSmallOffers, key=lambda smallOffer: smallOffer[11], reverse=True)  
                    thisGameBestOffer = thisGameSmallOffers[0]  # 排序后选第一个
                    # 把本场比赛最好的offer加到全局储存容器内,这些数据可以用来更新，不全部可以用来创建
                    allGameBestOffers.append(thisGameBestOffer)
                    # thisGameBestPosition = max(thisGameSmallPositions)
                    # lowestSmallOdd = thisGameSmallOffers[-1] #暂时用不上,之后可能算法会改