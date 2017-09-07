# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name: wdisplayer.py
   Description: 在屏幕上显示信息
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

import ctypes  

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

def cPrint(msg,color): #实现彩色打印
	
	ctypes.windll.Kernel32.GetStdHandle.restype = ctypes.c_ulong  
	h = ctypes.windll.Kernel32.GetStdHandle(ctypes.c_ulong(0xfffffff5))  
	if isinstance(color, int) == False or color < 0 or color > 15:  
		color = COLOR.SILVER #  
	ctypes.windll.Kernel32.SetConsoleTextAttribute(h, color)  
	print msg
	ctypes.windll.Kernel32.SetConsoleTextAttribute(h, COLOR.SILVER) 

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

def Information():
	if len(reports)>0:
		for report in reports:
			print report,
		print "\n"

def display_offer(info):
    