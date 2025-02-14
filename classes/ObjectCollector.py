from .GameObject import *
from typing import Callable

class Request:
    def __init__(self, isGood: Callable[[GameObject], bool], massage: str, num=1):
        self.isGood = isGood
        self.massage = massage
        self.num = num

        self.res: list[GameObject] = []
        self.resolved = False

class ObjectCollector:
    def __init__(self, gm):
        self.gm = gm
        self.queue: list[Request] = []

    def isCollecting(self):
        return len(self.queue) > 0

    def sendRequest(self, rq: Request):
        self.queue.append(rq)

        while not rq.resolved:
            yield

        self.queue.pop(0)
        
        return rq.res

    def addObj(self, obj: GameObject):
        if len(self.queue) > 0:
            if (now := self.queue[0]).isGood(obj):
                if obj in now.res:
                    now.res.remove(obj)
                else:
                    now.res.append(obj)
            
            elif obj == 'next' and len(now.res) == now.num:
                now.resolved = True