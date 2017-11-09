# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: wconfig.py
   Description: 全局设定在这里
   Author: Dexter Chen
   Date：2017-10-20
-------------------------------------------------
"""
display_protocol = 5  # 定义哪种显示方法
log_protocol = 2  # 定义哪种记录方法
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
    "odds": "http://sb-jxf.prdasbbwla1.com/zh-cn/OddsService/GetOdds?",  # 信息页
    "login": "http://www.wellbet228.net/zh-cn/sportsbook.php",  # 登录页
    "add": "http://www.wellbet228.net/zh-cn/sportsbook.php",  # 添加页
    "bet": "http://www.wellbet228.net/zh-cn/sportsbook.php",  # 下注页
    "balance": "http://www.wellbet228.net/zh-cn/uc/user/user_info.php",  # 剩余金额
    "human": "http://www.wellbet228.net/zh-cn/sportsbook.php"  # 正常浏览
}

# 是否第一次读取，如果是，强制获得球队名称等信息。未来改为“非第一次”加快速度
isFirstLoad = "true"
# 标记两种数据更新请求: ture,只请求更新inplay区域的; false,更新整页
isInplay = "true"


def set_config(mode):
    if mode == "1":  # 浏览模式:和自动一样,只是不真正下单,用于检验程序的可行性
        mimic = True

    elif mode == "2":  # 自动完成判断和下单
        autoBet = True
        autoBetNeedConfirm = True

    elif mode == "3":  # 自动完成判断,下单前要确认,回车才下
        autoBet = True

    elif mode == "4":  # 最大准许条件,让程序试错
        showError = True
        mimic = True
        loopTime = 10  # 把刷新时间加快
        writeLoop = 3  # 把记录所需循环数减少
        useLeagueWhiteList = False  # 不使用白名单
        mimicWaitTime = 0  # 下单不等待
        secondBetWaitTime = 40
        earliestAddTime = "00:00"  # 最早加入
        latestAddTime = "80:00"  # 最迟加入
        latestUpdateTime = "85:00"  # 最迟更新
        earliestFirstBetTime = "00:00"  # 最早首注
        latestFirstBetTime = "85:00"  # 最迟首注
        earlistSecondBetTime = "00:00"  # 最早补注
        latestSecondBetTime = "85:00"  # 最迟补注
