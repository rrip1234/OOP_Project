from enum import Enum, auto
from abc import ABCMeta, abstractmethod
from turtle import update

from discord import Game
from GameManager import GameManager, Pos, State, Phase
from CardList import *
from classes import *

scene = None
screen: pygame.Surface

class GameState(Enum):
    MAIN = auto()
    PLAY = auto()
    RESULT = auto()
    EDIT = auto()

def StartScene(next: GameState):
    global scene, screen

    if next is GameState.MAIN:
        scene = MainScene()
    elif next is GameState.PLAY:
        scene = PlayScene()
    elif next is GameState.RESULT:
        scene = ResultScene()
    elif next is GameState.EDIT:
        scene = DeckSceen()

FONT_COLOR = (42, 36, 31)
FONT_COLOR2 = (32, 26, 21)

MIN_DECK_SIZE = 18
MAX_DECK_SIZE = 24
MAX_CARD_NUM = 9

ENEMY_DECK = ['pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
ENEMY_PIECE = [False, True, False, True, False, True, False, True, False, True, False, True]

deck: list[str] = []
pieces: list[bool] = [False] * 12

def getFont(num):    
    if num == 0:
        return pygame.font.Font("batang.ttc", 30)
    elif num == 1:
        return pygame.font.Font("batang.ttc", 17)
    else:
        return pygame.font.SysFont("batang.ttc", 24, italic=True)

def makeDeck(deck_list: list[str]):
    res: list[CardObject] = []

    cardDB = GetCards()

    for code, card_name in enumerate(deck_list):
        res.append(CardObject(cardDB[card_name], str(code), (0, 0)))
    
    return res

text_dict = {}

def makeMultiLineText(name, font, text, limit, color, is_english):
    if name in text_dict:
        return text_dict[name]
    
    text_list = []

    if is_english:
        splited = text.split(' ')
        temp = ''
        for txt in splited:
            splited2 = txt.split('-')
            for i in range(len(splited2)):
                if len(temp + splited2[i]) <= limit:
                    temp += splited2[i]
                else:
                    if i != 0:
                        temp += '-'
                    text_list.append(font.render(temp, True, color))
                    temp = splited2[i]
                    
            temp += ' '
        text_list.append(font.render(temp, True, color))
    else:
        temp = ''
        cnt = 0
        shorts = [' ' , ',', '.']
        for txt in text:
            if txt in shorts:
                temp += txt
                cnt += 1
            
            if cnt >= limit - 1:
                text_list.append(font.render(temp, True, color))
                temp = ''
                cnt = 0
                if txt == ' ':
                    continue

            if txt not in shorts:
                temp += txt
                cnt += 2
    
        text_list.append(font.render(temp, True, color))
        
    text_dict[name] = text_list
    return text_list

def setBigCard(card_obj: GameObject, info):
    name, cost, script, subtext, image = info

    card_obj.original = pygame.transform.smoothscale(image, (250, 360))

    card_name = getFont(0).render(name, True, FONT_COLOR)
    card_cost = getFont(1).render(f"cost: {cost}", True, FONT_COLOR)
    card_text = makeMultiLineText(name + 'text', getFont(1), script, 38, FONT_COLOR, False) \
                + makeMultiLineText(name + 'subtext', getFont(2), subtext, 36, FONT_COLOR2, True)

    return (card_name, card_cost, card_text)

def makeObject(img, code, pos, size=None):
    if isinstance(img, str):
        img = pygame.image.load(img)
    if size is not None:
        img = pygame.transform.smoothscale(img, size)
    obj = GameObject(img, code, pos)
    return obj

class Scene(metaclass=ABCMeta):
    def update(self):
        events: dict[int, pygame.event.Event] = {}

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            else:
                events[event.type] = event
        
        updateCoroutine()
        
        return self.lateUpdate(events)

    @abstractmethod
    def lateUpdate(self, events: dict[int, pygame.event.Event]):
        pass

class MainScene(Scene):
    obj_list: list[GameObject] = []

    def __init__(self):
        self.title = makeObject("images/wowow.jpg", "title", (200, 200))
        self.obj_list.append(self.title)

        self.start_btn = makeObject("images/start_button.png", "start", (1240, 700))
        self.obj_list.append(self.start_btn)

        self.edit_button = makeObject("images/edit_button.png", "edit", (200, 700))
        self.obj_list.append(self.edit_button)

    def lateUpdate(self, events):
        if pygame.MOUSEBUTTONDOWN in events:
            event = events[pygame.MOUSEBUTTONDOWN]
            if self.start_btn.rect.collidepoint(event.pos):
                if MIN_DECK_SIZE <= len(deck) and len(deck) <= MAX_DECK_SIZE:
                    StartScene(GameState.PLAY)
                    return
                print("Deck Count Error")
            if self.edit_button.rect.collidepoint(event.pos):
                StartScene(GameState.EDIT)
                return

        for obj in self.obj_list:
            obj.draw(screen)            
        
        return

CARD_SIZE = 0.125
BIG_SIZE = 0.25

class PlayScene(Scene):
    def __init__(self):
        self.obj_list: list[GameObject] = []
        self.clicked_obj = None

        self.gm = GameManager(makeDeck(deck), pieces, makeDeck(ENEMY_DECK), ENEMY_PIECE, 5, True)
        self.setInitState(self.gm)
        
        self.back_btn = makeObject("images/back_button.png", "back_edit", (100, 850), (150, 75))
        self.obj_list.append(self.back_btn)
        
        self.next_btn = makeObject("images/next_button.png", "next", (1300, 150), (150, 75))
        self.obj_list.append(self.next_btn)

        self.ok_btn = makeObject("images/ok_button.png", "ok", (1200, 250), (50, 50))
        self.obj_list.append(self.ok_btn)

        self.wow_btn = makeObject("images/wowow.jpg", "up", (1300, 250), (50, 50))
        self.obj_list.append(self.wow_btn)

        self.temp_img = pygame.image.load('images/temp.png')
        self.big_card = makeObject(self.temp_img, "big", (150, 400))
        self.big_card.scale = BIG_SIZE
    
    def setInitState(self, gm: GameManager):
        for row in gm.board:
            for piece in row:
                piece.draw(screen)

        for pos in [Pos.P_HAND, Pos.E_HAND, Pos.P_LAND, Pos.E_LAND, Pos.P_DECK, Pos.E_DECK]:
            gm.updateObjState(pos)

    def showPlayScreen(self, gm: GameManager):
        focused = None
        
        for row in gm.board:
            for board in row:
                board.draw(screen)

        p_hand = gm.field_pos[Pos.P_HAND]
        for i, card_obj in enumerate(p_hand.cards):
            if card_obj.is_clicked:
                focused = card_obj
            card_obj.draw(screen)

        e_hand = gm.field_pos[Pos.E_HAND]
        for i, card_obj in enumerate(e_hand.cards):
            card_obj.draw(screen)
        
        if len(p_deck := gm.field_pos[Pos.P_DECK].cards) > 0:
            p_deck[-1].draw(screen)
            
        if len(e_deck := gm.field_pos[Pos.E_DECK].cards) > 0:
            e_deck[-1].draw(screen)

        p_cemetery = gm.field_pos[Pos.P_CEMETERY]
        for i, card_obj in enumerate(p_cemetery.cards):
            if card_obj.is_clicked:
                focused = card_obj
            card_obj.draw(screen)
        
        e_cemetery = gm.field_pos[Pos.E_CEMETERY]
        for i, card_obj in enumerate(e_cemetery.cards):
            if card_obj.is_clicked:
                focused = card_obj
            card_obj.draw(screen)

        p_land = gm.field_pos[Pos.P_LAND]
        for i, card_obj in enumerate(p_land.cards):
            if card_obj.is_clicked:
                focused = card_obj
            card_obj.draw(screen)
        
        e_land = gm.field_pos[Pos.E_LAND]
        for i, card_obj in enumerate(e_land.cards):
            card_obj.draw(screen)
        
        self.big_card.original = self.temp_img

        if focused is not None:
            focused.draw(screen)

            info = setBigCard(self.big_card, focused.info())

            screen.blit(info[0], (50, 600))
            screen.blit(info[1], (50, 640))
            for i, text in enumerate(info[2]):
                screen.blit(text, (50, 675 + i * 30))

        self.big_card.draw(screen)
    
    def checkClick(self, gm: GameManager, click_pos):
        if self.back_btn.rect.collidepoint(click_pos):
            StartScene(GameState.MAIN)
            return
        
        new_clicked = None

        if self.next_btn.rect.collidepoint(click_pos):
            new_clicked = self.next_btn

        if self.ok_btn.rect.collidepoint(click_pos):
            new_clicked = self.ok_btn

        if self.wow_btn.rect.collidepoint(click_pos):
            new_clicked = self.wow_btn

        for pos in [Pos.P_HAND, Pos.P_CEMETERY]:
            for card in gm.field_pos[pos].cards:
                if card.rect.collidepoint(click_pos):
                    new_clicked = card

        if gm.state in [State.HAND]:
            if gm.field_pos[Pos.P_LAND].rect.collidepoint(click_pos):
                new_clicked = gm.field_pos[Pos.P_LAND]
        else:
            for land in gm.field_pos[Pos.P_LAND].cards:
                if land.rect.collidepoint(click_pos):
                    new_clicked = land
        
        for row in gm.board:
            for board in row:
                if board.rect.collidepoint(click_pos):
                    new_clicked = board
        
        gm.manageEvent(new_clicked)

    def setGlow(self, gm: GameManager):
        for pos in [Pos.P_HAND, Pos.E_HAND, Pos.P_CEMETERY, Pos.E_CEMETERY, Pos.P_LAND, Pos.E_LAND]:
            for cd in gm.field_pos[pos].cards:
                cd.is_glow = False
        for row in gm.board:
            for board in row:
                board.is_glow = False

        if gm.phase is Phase.Land:
            for pos in [Pos.P_HAND, Pos.P_LAND]:
                for cd in gm.field_pos[pos].cards:
                    cd.is_glow = True

        elif gm.phase is Phase.Main:
            if gm.collector.isCollecting():
                for pos in [Pos.P_HAND, Pos.E_HAND, Pos.P_CEMETERY, Pos.E_CEMETERY, Pos.P_LAND, Pos.E_LAND]:
                    for cd in gm.field_pos[pos].cards:
                        cd.is_glow = gm.collector.isGood(cd)
                for row in gm.board:
                    for board in row:
                        board.is_glow = gm.collector.isGood(board)
            else:
                for cd in gm.field_pos[Pos.P_HAND].cards:
                    cd.is_glow = cd.base.isActivable(gm)
        
        elif gm.phase is Phase.Piece:
            if gm.state is State.NONE:
                for row in gm.board:
                    for board in row:
                        board.is_glow = (piece := board.piece) is not None and piece.is_mine and piece.card is not None
            elif gm.state is State.PIECE:
                for i in range(6):
                    for j in range(6):
                        gm.board[i][j].is_glow = (i, j) in gm.accessable

    def lateUpdate(self, events):
        if pygame.MOUSEBUTTONUP in events:
            self.checkClick(self.gm, events[pygame.MOUSEBUTTONUP].pos)

        now_phase = getFont(2).render(self.gm.phase.value, True, FONT_COLOR)
        screen.blit(now_phase, (1250, 50))

        updateCoroutine()

        self.setGlow(self.gm)
        
        for pos in [Pos.P_HAND, Pos.E_HAND, Pos.P_LAND, Pos.E_LAND, Pos.P_DECK, Pos.E_DECK, Pos.P_CEMETERY, Pos.E_CEMETERY]:
            self.gm.updateObjState(pos)

        for row in self.gm.board:
            for board in row:
                self.gm.updateObjState(board)
        
        for obj in self.obj_list:
            obj.draw(screen)
        
        self.showPlayScreen(self.gm)
        
        return None

class DeckSceen(Scene):
    def __init__(self):
        self.obj_list: list[GameObject] = []
        self.card_objs: dict[str, GameObject] = {}
        self.deck_objs: list[GameObject] = []
        self.deck: list[str] = deck

        self.temp_img = pygame.transform.smoothscale(pygame.image.load("images/temp.png"), (300, 432))
        self.big_card = makeObject(self.temp_img, "big_edit", (200, 266))
        self.obj_list.append(self.big_card)

        self.back_btn = makeObject("images/back_button.png", "back_edit", (1340, 800), (150, 75))
        self.obj_list.append(self.back_btn)

        self.empty_surface = pygame.Surface((120, 180), pygame.SRCALPHA)
        for i in range(MAX_DECK_SIZE):
            self.deck_objs.append(makeObject(self.empty_surface, f"deck_card{i}", (500 + 121 * (i % 6), 140 + 181 * (i // 6))))
        
        self.cardDB = GetCards()
        for name in self.cardDB:
            self.card_objs[name] = makeObject(self.cardDB[name].image, name, (0, 0), (150, 216))

        self.scroll_len = 0
    
    def lateUpdate(self, events):
        click_pos = None

        if pygame.MOUSEBUTTONDOWN in events:
            event = events[pygame.MOUSEBUTTONDOWN]
            if event.button == 1:
                if self.back_btn.rect.collidepoint(event.pos):
                    global deck#, pieces
                    deck = self.deck
                    #pieces = self.pieces
                    StartScene(GameState.MAIN)
                    return
                click_pos = event.pos
            elif event.button >= 4:
                self.scroll_len += (event.button * 2 - 9) * 50
                self.scroll_len = max(0, min((len(self.cardDB) - 3) * 217, self.scroll_len))

        for obj in self.obj_list:
            obj.draw(screen)

        for i in range(len(self.deck_objs)):
            if i < len(self.deck):
                self.deck_objs[i].original = pygame.transform.smoothscale(self.cardDB[self.deck[i]].image, (120, 180))
            else:
                self.deck_objs[i].original = self.empty_surface
        
        for obj in self.deck_objs:
            obj.draw(screen)

        mouse_pos = pygame.mouse.get_pos()

        self.big_card.original = self.temp_img

        for i, name in enumerate(self.card_objs):
            temp_card = self.card_objs[name]
            temp_card.position = (1315, i * 217 - self.scroll_len + 158)
            temp_card.draw(screen)
            
            if temp_card.rect.collidepoint(mouse_pos):
                info = setBigCard(self.big_card, self.cardDB[name].info())
                
                screen.blit(info[0], (50, 500))
                screen.blit(info[1], (50, 540))
                for i, text in enumerate(info[2]):
                    screen.blit(text, (50, 575 + i * 30))
            
            if click_pos is not None and temp_card.rect.collidepoint(click_pos):
                if self.deck.count(name) <= MAX_CARD_NUM and len(self.deck) < MAX_DECK_SIZE:
                    self.deck.append(name)
        
        for i, name in enumerate(self.deck):
            temp_card = self.deck_objs[i]
            if temp_card.rect.collidepoint(mouse_pos):
                info = setBigCard(self.big_card, self.cardDB[name].info())
                
                screen.blit(info[0], (50, 500))
                screen.blit(info[1], (50, 540))
                for j, text in enumerate(info[2]):
                    screen.blit(text, (50, 575 + j * 30))

            if click_pos is not None and temp_card.rect.collidepoint(click_pos):
                self.deck.pop(i)

        return None

class ResultScene(Scene):
    def __init__(self):...

    def lateUpdate(self, events):
        return None
