import math
import random
from operator import add
from numpy import isin
import pygame
from .Card import *

class GameObject(pygame.sprite.Sprite):
    def __eq__(self, other):
        if isinstance(other, GameObject):
            return self.code == other.code
        if isinstance(other, str):
            return self.code == other
        return False

    def __init__(self, image: pygame.surface.Surface, code, pos):
        super().__init__()
        self.code = code
        self.rect = image.get_rect(center = pos)
        self.is_clicked = False
        
        self.original = image
        self.image = None
        self.rect = self.original.get_rect()
        self.size = tuple(map(float, self.rect.size))

        self.scale = 1.0
        self.angle = 0.0
        self.position = pos
    
    def update_image(self):
        img = self.original.copy()
        if self.scale != 0:
            img = pygame.transform.scale(img, tuple([int(self.scale * x) for x in self.size]))
        if self.angle != 1:
            img = pygame.transform.rotate(img, self.angle)
            
        self.rect = img.get_rect()
        self.rect.center = self.position
        self.image = img
    
    def draw(self, screen):
        self.update_image()
        screen.blit(self.image, self.rect)

class CardObject(GameObject):
    def __init__(self, base_card: BaseCard, code: str, pos):
        super().__init__(base_card.image, code, pos)
        self.base = base_card

        self.back_image = pygame.image.load('images/temp.png')
        self.outline = pygame.image.load('images/card_outline.png')
        self.outline_selected = pygame.image.load('images/card_outline_selected.png')
        self.glow_size = (self.size[0] + 150, self.size[1] + 120)

        self.is_front = True
        self.is_moving = False
        self.is_glow = False

    def info(self):
        return self.base.info()
    
    def myType(self):
        if isinstance(self.base, RoleCard):
            return RoleCard
        elif isinstance(self.base, SpecialCard):
            return SpecialCard
        else:
            return BaseCard
    
    def update_image(self):
        if self.is_glow:
            img = (self.outline_selected if self.is_clicked else self.outline)
            img.blit(self.original if self.is_front else self.back_image, (75, 60))
        else:
            img = self.original if self.is_front else self.back_image
        
        if self.scale != 0:
            img = pygame.transform.scale(img, tuple([int(self.scale * x) for x in (self.glow_size if self.is_glow else self.size)]))
        if self.angle != 1:
            img = pygame.transform.rotate(img, self.angle)
        self.rect = img.get_rect()
        self.rect.center = self.position
        self.image = img
        
class PieceObject(GameObject):
    def __init__(self, image, code, pos, is_mine: bool):
        super().__init__(image, code, pos)
        self.is_mine = is_mine

        self.card = None
        self.direction = None
        self.cdImg = None
        self.cnt = 0

        self.is_moved = False
        self.card_changed = False
    
    def draw(self, screen):
        self.update_image()
        if self.card is not None:
            screen.blit(self.cdImg, self.rect.topleft, (4, 20.5, 79, 95.5))
        screen.blit(self.image, self.rect)

    def addCard(self, cd: CardObject):
        if isinstance(cd.base, RoleCard):
            self.card_changed = True
            self.card = cd
            self.direction = cd.base.direction
            self.cdImg = pygame.transform.scale(cd.image, (83.33, 120))
    
    def getCard(self):
        res = self.card
        self.card = None
        self.direction = None
        return res

class BoardObject(GameObject):
    def __init__(self, image: pygame.surface.Surface, code, x: int, y: int):
        pos = (495 + 90 * y, 225 + 90 * x)
        super().__init__(image, code, pos)

        self.x = x
        self.y = y

        self.outline = pygame.image.load('images/board_outline.png')
        self.outline_selected = pygame.image.load('images/board_outline_selected.png')
        self.piece = None
        self.glow_size = (110, 110)

        self.is_glow = False

    def getPiece(self):
        res = self.piece
        self.piece = None
        return res
    
    def addPiece(self, piece: PieceObject):
        self.piece = piece

    def update_image(self):
        if self.is_glow:
            img = (self.outline_selected if self.is_clicked else self.outline)
            img.blit(self.original, (10, 10))
        else:
            img = self.original
        
        if self.scale != 0:
            img = pygame.transform.scale(img, tuple([int(self.scale * x) for x in (self.glow_size if self.is_glow else self.size)]))
        if self.angle != 1:
            img = pygame.transform.rotate(img, self.angle)
        self.rect = img.get_rect()
        self.rect.center = self.position
        self.image = img

    def draw(self, screen):
        self.update_image()
        screen.blit(self.image, self.rect)
        if self.piece is not None:
            self.piece.draw(screen)

class Zone(GameObject):    
    def __init__(self, image, code, pos, is_enemy, angle, scale, is_front):
        super().__init__(image, code, pos)
        self.cards: list[CardObject] = []

        self.num = 0
        self.is_enemy = is_enemy

        self.angle = angle
        self.scale = scale
        self.is_front = is_front
        self.is_glow = False

    def getPos(self, i, num=-1):
        x, y = self.position

        if self.is_enemy:
            x = -x
            y = -y

        return x, y

    def nextPos(self):
        return self.getPos(self.num, self.num + 1)
    
    def getCard(self, target):
        if isinstance(target, int):
            self.num -= 1
            return self.cards.pop(target)
        if isinstance(target, GameObject):
            for cd in self.cards:
                if cd == target:
                    res = cd
                    self.cards.remove(cd)
                    self.num -= 1
                    return res
            return None
    
    def addCard(self, cardObj):
        if isinstance(cardObj, CardObject):
            self.num += 1
            self.cards.append(cardObj)
        elif isinstance(cardObj, list):
            self.num += len(cardObj)
            self.cards.extend(cardObj)
    
    def shuffle(self):
        random.shuffle(self.cards)
        
    def update(self, screen):
        super().draw(screen)
        for i, cd in enumerate(self.cards):
            cd.position = self.getPos(i)

class DeckZone(Zone):
    def addCard(self, cardObj):
        if isinstance(cardObj, CardObject):
            self.num += 1
            self.cards.insert(0, cardObj)
        elif isinstance(cardObj, list):
            self.num += len(cardObj)
            self.cards = cardObj + self.cards

class HandZone(Zone):
    def getPos(self, i, num=-1):
        if num == -1:
            num = self.num
        
        x = (i - num / 2 + 0.5) * 60
        y = 360

        if self.is_enemy:
            x = -x
            y = -y
            
        return (720 + x, 450 + y)
    
class CemeteryZone(Zone):
    def getPos(self, i, num=-1):
        
        x = 600 + (i // 9) * 10 - (i % 9) * 35
        y = 310 + (i // 9) * 25

        if self.is_enemy:
            x = -x
            y = -y

        return (720 + x, 450 + y)

class LandZone(Zone):
    def getPos(self, i, num=-1):
        if num == -1:
            num = self.num
        
        x = 530
        y = 225 - i * 30

        if self.is_enemy:
            x = -x
            y = -y
        
        return (720 + x, 450 + y)