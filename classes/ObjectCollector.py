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
        for obj in rq.res:
            obj.is_clicked = False
        
        return rq.res

    def isGood(self, obj):
        return self.queue[0].isGood(obj)

    def addObj(self, obj: GameObject):
        if len(self.queue) > 0:
            if (now := self.queue[0]).isGood(obj):
                if obj in now.res:
                    obj.is_clicked = False
                    now.res.remove(obj)
                elif len(now.res) < now.num:
                    obj.is_clicked = True
                    now.res.append(obj)
            
            elif obj == 'ok' and len(now.res) == now.num:
                now.resolved = True