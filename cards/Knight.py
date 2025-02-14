from CardList import *

name = '은빛 창의 기사 리아논'
short = 'knight'
cost = 4
script = '은빛 창의 기사 리아논은, 한 번에 세 걸음 움직이며, 다른 이들을 지나칠 수 있고, 원래 위치와 같은 행 또는 열로는 갈 수 없다.'
subscript = ''
direction = DirInfo(dir=[1, 0, 1, 0, 1, 0, 1, 0], mn=3, mx=3, can_jump=True, can_str=False)

AddCard(name, short, cost, script, subscript, direction)