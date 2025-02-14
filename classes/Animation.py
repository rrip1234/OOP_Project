import pytweening
from enum import Enum, auto
from .Coroutine import waitForSeconds

class LoopType(Enum):
    No = auto()
    Incremental = auto()
    Restart = auto()
    Yoyo = auto()

def lerpVector(a: tuple[float, float], b: tuple[float, float], t: float):
    x = a[0] * (1 - t) + b[0] * t
    y = a[1] * (1 - t) + b[1] * t
    return (x, y)

def lerpFloat(a: float, b: float, t: float):
    return a * (1 - t) + b * t

def DOMove(obj, target: tuple[int, int], time, func, repeat=LoopType.No, loops=-1):
    t = 0
    init_pos = obj.position
    obj.is_moving = True

    while t < 1:
        obj.position = (init_pos[0] + (target[0] - init_pos[0]) * func(t), init_pos[1] + (target[1] - init_pos[1]) * func(t))
        t += 0.02 / time
        yield from waitForSeconds(0.02)
    
    obj.is_moving = False