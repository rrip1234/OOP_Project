from CardList import *

name = '성도의 주교 베일리온'
short = "bishop"
cost = 3
script = '성도의 주교 베일리온은 일직선으로 두 걸음까지 움직일 수 있다.'
subscript = ''
direction = DirInfo(dir=[0, 1, 0, 1, 0, 1, 0, 1], mx=2, can_str=False)

AddCard(name, short, cost, script, subscript, direction)