#!/bin/env python3
# -*- coding: utf-8 -*-

from turtle import *

# 设置笔刷宽度
width(4)

# 前进
forward(200)
# 右转90度
right(90)

# 笔刷颜色
pencolor('red')
forward(100)
right(90)

pencolor('green')
forward(200)
right(90)

pencolor('blue')
forward(100)
right(90)

def drawStar(x, y):
    pu()
    goto(x, y)
    pd()
    # set heading: 0
    seth(0)
    for i in range(5):
        fd(40)
        rt(144)

for x in range(0, 250, 50):
    drawStar(0, x)

# 调用donw()使得窗口等待被关闭, 否则将立即关闭窗口
done()
