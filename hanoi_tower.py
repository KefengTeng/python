#!/bin/env python3
# -*- coding: utf-8 -*-

# 初始状态，所有的圆盘都在A柱上，最终都挪到C柱上【大圆盘不能放在小圆盘的上面】
def move(n, a, b, c):

    if n == 1:
        print(a, '-->', c)
    else:
	# A柱n-1个圆盘需要在B、C柱的配合下都挪到B柱
        move(n - 1, a, c, b)
        # A柱只留一个最大的圆盘，可以直接挪到C柱
        print(a, '-->', c)
        # B柱所有的盘子需要在A、B柱的配合下都挪到C柱
        move(n - 1, b, a, c)


if __name__ == '__main__':
    move(3, 'A', 'B', 'C')
