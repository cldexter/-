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
import agents
import mongodb_handler as mh
import message as msg
import dictionary as dic


reload(sys)
sys.setdefaultencoding('UTF-8')

# 定义全局变量


def get_raw_data():  # 发送数据更新请求,更新后的数据存在全局变量中
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
    tries = 2
    while tries > 0:
        try:
            # 抓回来的是解码json生成的dict文件
            response = requests.get(link, data=payload, headers=agents.get_header()).json()
            break
        except Exception, e:
            tries -= 1
    # 重新合成抓回来的数据
    iot_Leagues = []
    not_Leagues = []
    if 'egs' in response['i-ot'].keys():
        # 滚球信息dict,response的子集
        iot_Leagues = response['i-ot']['egs']
    if 'egs' in response['n-ot'].keys():
        # 今日信息dict,response的子集，已开始的比赛
        not_Leagues = response['n-ot']['egs']
    leagues = iot_Leagues + not_Leagues
    return leagues


def save_game_data(league_name, host_team, guest_team, league_k, game_k, game_date_time, game_pass_time, game_half, host_team_score, guest_team_score, position_big, odd_id_big, odd_big, position_small, odd_id_small, odd_small):
# 处理数据,很多层,小心每一层到底是list还是dict,dict就用['es'],list就一定搞遍历(for)
# 以下筛选可以关注的offer,目的是把所有可以投注的offer筛出来，然后让每个offer实体各自去更新
# 筛选offer交给函数，买不买交给对象
    game_record_new = {"add_time": ut.time_str("full"), "league_name": league_name, "host_team": host_team, "guest_team": guest_team, "league_k": league_k, "game_k": game_k}
    game_status_new = {"last_update": ut.time_str("full"), "game_k": game_k, "game_past_time": game_pass_time, "game_half": game_half, "host_team_score": host_team_score, "guest_team_score": guest_team_score, "position_big": position_big, "odd_id_big": odd_id_big, "odd_big": odd_big, "position_small": position_small, "odd_id_small": odd_id_small, "odd_small": odd_small}
    game_k_all = mh.read_game_k_all()
    if not game_k in game_k_all:
        mh.add_game_record(game_record_new, "game")
        mh.add_game_record(game_status_new, "status")
        msg.msg(u"新加比赛", host_team + guest_team, u"添加", u"succ", "info", msg.display)
    else:
        mh.add_game_record(game_status_new, "status")
        msg.msg(u"已有比赛", host_team + guest_team, u"更新","succ", "info", msg.display)


def get_all_offers(leagues):
    all_offer_small = []
    for league in leagues:
        league_k = league['c']['k']  # 联赛编号
        league_name = league['c']['n']  # 联赛名字
        for game in league['es']:  # 对每一场比赛,进行如下操作
            # thisGamesmall_offers = []  # 本场比赛所有small_offers合集,用于存放该轮选好的offer,最后排序后添加到大offer里面
            game_k = game['k']  # 比赛编号
            host_team = game['i'][0]  # 主队名字
            guest_team = game['i'][1]  # 客队名称
            game_date = game['i'][4]  # 比赛日期,格式 日/月
            game_pass_time = game['i'][5]  # 现在进行到多少时间,如果还没有开始就显示什么时候开始
            host_team_score = game['i'][10]  # 主队得分情况
            guest_team_score = game['i'][11]  # 客队得分情况
            if host_team_score == "":  # 没有得分的，说明日期是比赛开始日期
                game_date_time = ut.time_str_converter(game_date, game_pass_time)
                game_pass_time = "00:00"
            else:
                game_date_time = u"进行中"
            game_half_raw = game['i'][12]  # 上下半场,中场TH,用于判断比赛是否开始
            if game_half_raw == "" and host_team_score != "":  # 比赛已经开始了
                game_half = u"暂停"
            else:
                game_half = ut.dict_replace(game_half_raw, dic.dict_game_stage)
            # save_game_data(league_name, host_team, guest_team, league_k, game_k, game_date_time, game_pass_time, game_half, host_team_score, guest_team_score)
            if 'ou' in game['o'].keys():  # 如果有买大小的盘口的话
                game_offer_small_list = [] # 把所有可以买小的offer都列在这里
                offer_number = len(game['o']['ou']) / 8  # 到底有多少组offer
                i = 0
                for item in range(0, offer_number):  # 生成多个bet offer
                    position_big = game['o']['ou'][i * 8 + 1]  # 买大盘口[1]
                    # 买小盘口[3]和主队盘口应该完全一样
                    position_small = game['o']['ou'][i * 8 + 3]
                    odd_id_big = game['o']['ou'][i * 8 + 4]  # 买大赔率编号[4]
                    odd_big = game['o']['ou'][i * 8 + 5]  # 买大赔率[5]
                    odd_id_small = game['o']['ou'][i * 8 + 6]  # 买小赔率编号[6]
                    odd_small = game['o']['ou'][i * 8 + 7]  # 买小赔率[7]
                    # 买小（small_offer）是我们玩的主要东西
                    print position_big
                    print position_small
                    print odd_small
                    print "-"
                    if (not "/" in position_big) and (position_small > 0) and (odd_small > 0):
                        offer_small = (game_k, game_pass_time, game_half, host_team_score, guest_team_score, position_big, odd_id_big, odd_big, position_small, odd_id_small, odd_small)
                        game_offer_small_list.append(offer_small)
                    i += 1
                if len(game_offer_small_list) > 0:
                    max_offer_small = sorted(game_offer_small_list, key=lambda offer_small:offer_small[9],reverse=True)[0] # 找到最大的offer_samll
                    print "max_offer:" + max_offer_small[8]
                    save_game_data(league_name, host_team, guest_team, league_k, game_k, game_date_time, offer_small[1], offer_small[2], offer_small[3], offer_small[4], offer_small[5], offer_small[6], offer_small[7], offer_small[8], offer_small[9], offer_small[10])

def league_filter(league_name):
    '''在这里编写选联赛的条件'''
    key_words = []
    for key_word in key_words:
        if key_words in league_name:
            return False
    else:
        return True


def game_filter(game_name)


if __name__ == "__main__":
    get_all_offers(get_raw_data())
