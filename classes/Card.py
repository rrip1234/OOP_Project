from typing import Callable

class DirInfo:
    def __init__(self,
                 dir=[0] * 8,
                 mn=1,
                 mx=1,
                 can_jump=False,
                 can_str=True,
                 can_dia=True):
        
        self.dir = dir
        self.mn = mn
        self.mx = mx
        self.can_jump = can_jump
        self.can_str = can_str
        self.can_dia = can_dia

class BaseCard:
    def __init__(self, name, cost, script, subscript, image, precon, abillity):
        self.name = name
        self.cost = cost
        self.script = script
        self.subscript = subscript
        self.image = image
        self.isActivable = precon
        self.ability = abillity
    
    def info(self):
        return self.name, self.cost, self.script, self.subscript, self.image

class RoleCard(BaseCard):
    def __init__(self, name, cost, script, subscript, precon, abillity, direction: DirInfo, image):
        super().__init__(name, cost, script, subscript, image, precon, abillity)
        self.direction = direction

class SpecialCard(BaseCard):
    def __init__(self, name, cost, script, subscript, precon: Callable, abillity: Callable, image):
        super().__init__(name, cost, script, subscript, image, precon, abillity)