import os
from classes import *
from GameManager import GameManager
import pygame

cardDB: dict[str, BaseCard] = {}

def GetCards():
    if len(cardDB) > 0:
        return cardDB
    
    for filename in os.listdir('cards'):
        exec(open('cards/' + filename).read())

    return cardDB

def AddCard(name, short, cost, script, subscript, abillity, precon=(lambda obj: True)):
    if isinstance(abillity, DirInfo):
        cardDB[short] = RoleCard(name, cost, script, subscript, abillity, pygame.image.load(f"images/{short}.png"))
    elif callable(abillity):
        cardDB[short] = SpecialCard(name, cost, script, subscript, precon, abillity, pygame.image.load(f"images/{short}.png"))