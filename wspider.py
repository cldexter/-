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

reload(sys)
sys.setdefaultencoding('UTF-8')

# 定义全局变量

def get_data():  # 发送数据更新请求,更新后的数据存在全局变量中
    # leagues是抓回来的数据容器
    global leagues
    # 选择哪个站点,吉祥坊和UED用的一套数据
    link = wconfig.siteUrls['odds']
    # 定义链接请求参数，已调好，不要动
    payload = {
        "_": ut.time_stamp(),
        "moreBetEvent": wconfig.moreBetEvent,
        "isFirstLoad": wconfig.isFirstLoad,
        "uiBetType": wconfig.uiBetType,
        "programmeId": wconfig.programmeId,
        "pageType": wconfig.pageType,
        "sportId": wconfig.sportId
    }
    # 抓回来的是解码json生成的dict文件
    response = requests.get(link, data=payload).json()
    # 重新合成抓回来的数据
    if 'egs' in response['i-ot'].keys():
        # 滚球信息dict,response的子集
        iotLeagues = response['i-ot']['egs']
    if 'egs' in response['n-ot'].keys():
        # 今日信息dict,response的子集，已开始的比赛
        notLeagues = response['n-ot']['egs']
    leagues = iotLeagues + notLeagues
    return leagues

# 处理数据,很多层,小心每一层到底是list还是dict,dict就用['es'],list就一定搞遍历(for)
# 以下筛选可以关注的offer,目的是把所有可以投注的offer筛出来，然后让每个offer实体各自去更新
# 筛选offer交给函数，买不买交给对象
def clean_data(leagues):
    for league in leagues:
        leagueK = league['c']['k']  # 联赛编号
        leagueName = league['c']['n']  # 联赛名字
        for game in league['es']:  # 对每一场比赛,进行如下操作
            # 本场比赛所有smalloffers合集,用于存放该轮选好的offer,最后排序后添加到大offer里面
            thisGameSmallOffers = []
            gameK = game['k']  # 比赛编号
            hostTeam = game['i'][0] # 主队名字
            awayTeam = game['i'][1]# 客队名称
            gameDate = game['i'][4]  # 比赛日期,格式 日/月
            gameTime = game['i'][5]  # 现在进行到多少时间,如果还没有开始就显示什么时候开始
            hostTeamScore = game['i'][10]  # 主队得分情况
            awayTeamScore = game['i'][11]  # 客队得分情况
            gameHalf = game['i'][12]  # 上下半场,中场TH,用于判断比赛是否开始
            if 'ou' in game['o'].keys(): # 如果有买大小的盘口的话
                offerNumber = len(game['o']['ou']) / 8  # 到底有多少组offer
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
                    smallOdds = game['o']['ou'][i * 8 + 7]                    # 如下是offer必须符合的几个条件
                    # 买小（smallOffer）是我们玩的主要东西
                    # smallOffer = leagueK, gameK, gameDate, gameTime, gameHalf, hostTeamScore, awayTeamScore, bigPosition, smallPosition, bigOdds, smallOdds, bigOddsNumber, smallOddsNumber
                    smallOffer = {"leagueName":leagueName,"hostTeam":hostTeam, "awyTeam":awayTeam,"leagueK": leagueK, "gameK": gameK, "gameDate": gameDate, "gameTime": gameTime, "gameHalf": gameHalf, "hostTeamScore": hostTeamScore, "awayTeamScore": awayTeamScore,
                                  "bigOddId": bigOddsNumber, "bigPosition": bigPosition, "bigOdds": bigOdds, "smallOddId": smallOddsNumber, "smallPosition": smallPosition, "smallOdds": smallOdds}
                    # 把这个比赛所有小都凑到一起（一个比赛不止一个smallOffer）
                    print smallOffer
                    # print leagueName, hostTeam, awayTeam
                    i += 1


if __name__ == "__main__":
    clean_data(get_data())
