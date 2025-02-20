from enum import auto, Enum

class Pos(Enum):
    P_DECK = auto()
    P_HAND = auto()
    #P_STACK= auto()
    P_CEMETERY = auto()
    P_LAND = auto()
    
    E_DECK = auto()
    E_HAND = auto()
    #E_STACK = auto()
    E_CEMETERY = auto()
    E_LAND = auto()

class State(Enum):
    NONE = auto()
    HAND = auto()
    LAND = auto()
    ACTIVE = auto()
    PIECE = auto()

class Phase(Enum):
    Land = 'Cost Phase'
    Main = 'Main Phase'
    Piece = 'Move Phase'
    Enemy = 'Enemy Turn'