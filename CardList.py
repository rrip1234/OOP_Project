import os
from classes import *
from copy import deepcopy
from GameManager import GameManager
import pygame

cardDB: dict[str, BaseCard] = {}

def GetCards():
    if len(cardDB) > 0:
        return cardDB
    
    for filename in os.listdir('cards'):
        exec(open('cards/' + filename).read())

    return cardDB

def RoleAbillity(gm: GameManager, cd: CardObject):
    condition = lambda obj: isinstance(obj, BoardObject) and\
                            obj.piece is not None and\
                            obj.piece.is_mine and\
                            not obj.piece.card_changed

    request = Request(condition, "Choose one ally.", 1)

    piece = yield from gm.collector.sendRequest(request)

    if not isinstance(piece[0], BoardObject):
        return

    gm.moveCard(cd, Pos.P_HAND, piece[0].piece, 0) # type: ignore

def AddCard(name, short, cost, script, subscript, precon=None, abillity=None, dir=None):
    if dir is not None:
        precon = lambda gm: gm.cost >= cost
        abillity = deepcopy(RoleAbillity)
        cardDB[short] = RoleCard(name, cost, script, subscript, precon, abillity, dir, pygame.image.load(f"images/{short}.png"))
    elif precon is not None and abillity is not None:
        precon1 = lambda gm: gm.cost >= cost and precon(gm)
        cardDB[short] = SpecialCard(name, cost, script, subscript, precon1, abillity, pygame.image.load(f"images/{short}.png"))