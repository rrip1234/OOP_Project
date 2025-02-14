from queue import Queue
from operator import add
from typing import Union
from classes.ObjectCollector import ObjectCollector
from classes import *

class GameManager:
    def __init__(self, my_deck: list[CardObject], pieces: list[bool],
                 enemy_deck: list[CardObject], enepieces: list[bool],
                 initHand: int, is_first: bool):
        
        self.catched: list[int] = [0, 0]
        self.collector = ObjectCollector(self)
        self.cost = 0
        
        self.empty = pygame.Surface((120, 180), pygame.SRCALPHA)
        self.back = pygame.image.load('images/temp.png')

        self.field_pos: dict[Pos, Zone] = {Pos.P_DECK:             Zone(self.empty, "pdeck", (1100, 650), False, 0,  0.125, False),
                                           Pos.P_HAND:         HandZone(self.empty, "phand", (0, 800),    False, 0,  0.125, True),
                                           Pos.P_CEMETERY: CemeteryZone(self.empty, "pcmtr", (1200, 760), False, 0,  0.125, True),
                                           Pos.P_LAND:         LandZone(self.empty, "pland", (1250, 500), False, 90, 0.125, True),
                                           Pos.E_DECK:             Zone(self.empty, "edeck", (340, 250),  True, 180, 0.125, False),
                                           Pos.E_HAND:         HandZone(self.empty, "ehand", (0, 100),    True, 180, 0.125, False),
                                           Pos.E_CEMETERY: CemeteryZone(self.empty, "ecmtr", (200, 140),  True, 180, 0.125, True),
                                           Pos.E_LAND:         LandZone(self.empty, "eland", (190, 400),  True, 270, 0.125, False)}
        
        self.state = State.NONE
        self.phase = Phase.Land if is_first else Phase.Enemy
        self.buffer = None
        self.accessable: list[tuple[int, int]] = []
        self.is_turn_mine = is_first
        
        self.piece_img = pygame.transform.scale(pygame.image.load('images/wowow.jpg'), (50, 50))
        
        self.field_pos[Pos.P_DECK].addCard(my_deck)
        self.field_pos[Pos.E_DECK].addCard(enemy_deck)
        
        self.field_pos[Pos.P_DECK].shuffle()
        self.field_pos[Pos.E_DECK].shuffle()

        img1 =  pygame.transform.scale(pygame.image.load("images/grid1.png"), (90, 90))
        img2 =  pygame.transform.scale(pygame.image.load("images/grid2.png"), (90, 90))
        img = [img1, img2]

        self.board: list[list[BoardObject]] = []
        for i in range(6):
            self.board.append([])
            for j in range(6):
                board = BoardObject(img[(i + j) % 2], f"board{i}{j}", i, j)
                self.board[i].append(board)
        
        for _ in range(initHand):
            self.moveCard(-1, Pos.P_DECK, Pos.P_HAND, 0)
            self.moveCard(-1, Pos.E_DECK, Pos.E_HAND, 0)

        cnt = 0
        for i, is_true in enumerate(pieces):
            if is_true:
                x = 4 + i // 6
                y = i % 6
                cnt += 1
                self.board[x][y].addPiece(PieceObject(self.piece_img, f"piece{cnt}", (0, 0), True))

        cnt = 0
        for i, is_true in enumerate(enepieces):
            if is_true:
                x = 1 - i // 6
                y = 5 - i % 6
                self.board[x][y].addPiece(PieceObject(self.piece_img, f"piece{cnt}", (0, 0), False))

    def isExist(self, pos: Pos, obj: GameObject):
        return obj in self.field_pos[pos].cards
    
    def moveCard(self, obj, start: Union[Pos, PieceObject], end: Union[Pos, PieceObject], time, graph=pytweening.linear):
        if isinstance(start, PieceObject):
            cd = start.getCard()
        else:
            cd = self.field_pos[start].getCard(obj)
        
        if cd is None:
            return

        if time != 0:
            end_pos = end.position if isinstance(end, PieceObject) else self.field_pos[end].nextPos()
            startCoroutine(DOMove(cd, end_pos, time, graph))

        if isinstance(end, PieceObject):
            end.addCard(cd)
        else:
            self.field_pos[end].addCard(cd)

    dxy = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

    def is_good(self, ix:int, iy:int, x:int , y:int, moved:int, dir:DirInfo):
        if moved < dir.mn:
            return False
        if (piece := self.board[x][y].piece) is not None:
            if piece.is_mine:
                return False
        if (x == ix or y == iy) and not dir.can_str:
            return False
        if (x + y == ix + iy or x - y == ix - iy) and not dir.can_dia:
            return False
        return True

    def getAccessable(self, ix, iy, dir:DirInfo):
        res = []
        visited = []

        q: Queue[tuple[int, int, int]] = Queue()
        q.put((ix, iy, 0))

        while not q.empty():
            x, y, moved = q.get()

            if (x, y) not in res and self.is_good(ix, iy, x, y, moved, dir):
                res.append((x, y))

            if (moved != 0 and self.board[x][y].piece is not None and not dir.can_jump) or moved == dir.mx:
                continue                
            
            for i in range(8):
                if dir.dir[i] == 1:
                    nx, ny = x + self.dxy[i][0], y + self.dxy[i][1]
                    if 0 <= nx and nx < 6 and 0 <= ny and ny < 6 and (nx, ny) not in visited:
                        visited.append((nx, ny))
                        q.put((nx, ny, moved + 1))
        return res

    def updateObjState(self, pos, t=0.5):
        if isinstance(pos, BoardObject):
            if (piece := pos.piece)is not None:
                piece.position = lerpVector(piece.position, pos.position, t)
                if (cd := piece.card) is not None:
                    cd.position = lerpVector(cd.position, piece.position, t)
                    cd.angle = lerpFloat(cd.angle, piece.angle, t)

        elif isinstance(pos, Pos):
            zone = self.field_pos[pos]
            cards = zone.cards
            for i, cd in enumerate(cards):
                if not cd.is_moving:
                    if pos is Pos.P_HAND and cd.is_clicked:
                        cd.position = lerpVector(cd.position, tuple(map(add, zone.getPos(i), (0, -30))), t)
                    elif pos is Pos.P_LAND and self.cost > i:
                        cd.position = lerpVector(cd.position, tuple(map(add, zone.getPos(i), (40, 0))), t)
                    else:
                        cd.position = lerpVector(cd.position, zone.getPos(i), t)
                    cd.angle = lerpFloat(cd.angle, zone.angle, t)
                    cd.scale = lerpFloat(cd.scale, zone.scale, t)
                cd.is_front = zone.is_front

    def changePhase(self):
        if self.buffer is not None:
            self.buffer.is_clicked = False
            self.buffer = None

        if self.phase is Phase.Land:
            self.cost = len(self.field_pos[Pos.P_LAND].cards)
            if len(self.field_pos[Pos.P_DECK].cards) > 0:
                self.moveCard(-1, Pos.P_DECK, Pos.P_HAND, 0.3, pytweening.easeInOutBack)
            self.phase = Phase.Main
        elif self.phase is Phase.Main:
            self.phase = Phase.Piece
        elif self.phase is Phase.Piece:
            self.phase = Phase.Enemy
        elif self.phase is Phase.Enemy:
            self.phase = Phase.Land
            
    def manageEvent(self, obj):
        if isinstance(obj, GameObject) and obj.code == "up":
            self.cost += 1

        if self.buffer is not None:
            self.buffer.is_clicked = False

        if self.collector.isCollecting():
            self.collector.addObj(obj)

        elif isinstance(obj, GameObject) and obj.code == 'next':
            self.changePhase()

        elif self.phase is Phase.Land:
            if isinstance(obj, CardObject):
                if self.isExist(Pos.P_LAND, obj):
                    self.moveCard(obj, Pos.P_LAND, Pos.P_HAND, 0)
                elif self.isExist(Pos.P_HAND, obj):
                    self.moveCard(obj, Pos.P_HAND, Pos.P_LAND, 0)
            
        elif self.phase is Phase.Main:
            if self.state is State.NONE:
                if isinstance(obj, CardObject):
                    obj.is_clicked = True
                    if self.isExist(Pos.P_HAND, obj):
                        if isinstance(obj.card_info, RoleCard):
                            self.buffer = obj
                            self.state = State.ROLE
                        elif isinstance(obj.card_info, SpecialCard):
                            self.buffer = obj
                            self.state = State.SPECIAL

            elif self.state is State.ROLE:
                if not isinstance(self.buffer, CardObject):
                    return
                
                if isinstance(obj, BoardObject) and (piece := obj.piece) is not None and\
                   piece.is_mine and self.cost >= self.buffer.card_info.cost:
                    self.cost -= self.buffer.card_info.cost
                    if piece.card is not None:
                        self.moveCard('', piece, Pos.P_CEMETERY, 0)
                    self.moveCard(self.buffer, Pos.P_HAND, piece, 0.5, pytweening.easeOutBounce)
                    self.buffer = None
                    self.state = State.NONE
                elif isinstance(obj, CardObject) and self.isExist(Pos.P_HAND, obj):
                    obj.is_clicked = True
                    self.buffer = obj
                    if isinstance(obj.card_info, SpecialCard):
                        self.state = State.SPECIAL
                else:
                    self.buffer = None
                    self.state = State.NONE
            
            elif self.state is State.SPECIAL:
                if isinstance(self.buffer, CardObject):
                    if isinstance(obj, CardObject) and isinstance(obj.card_info, SpecialCard) and\
                       self.buffer == obj and obj.card_info.precon(self) and self.cost >= self.buffer.card_info.cost:
                    
                        self.cost -= self.buffer.card_info.cost
                        startCoroutine(obj.card_info.ability(self, obj))

                    elif isinstance(obj, CardObject) and self.isExist(Pos.P_HAND, obj):
                        obj.is_clicked = True
                        self.buffer = obj
                        if isinstance(obj.card_info, RoleCard):
                            self.state = State.ROLE
                    else:
                        self.buffer = None
                        self.state = State.NONE
        
        elif self.phase is Phase.Piece:
            if self.state is State.NONE:
                if isinstance(obj, BoardObject) and (piece := obj.piece) is not None\
                    and piece.is_mine and (direction := piece.direction) is not None:
                    
                    obj.is_clicked = True
                    self.buffer = obj
                    self.accessable = self.getAccessable(obj.x, obj.y, direction)
                    self.state = State.PIECE
            elif self.state is State.PIECE:
                if isinstance(obj, BoardObject):
                    if isinstance(self.buffer, BoardObject):
                        if (obj.x, obj.y) in self.accessable:
                            target = self.board[obj.x][obj.y]
                            if (piece := target.piece) is not None and not piece.is_mine:
                                if not piece.is_mine and piece.hasDir:
                                    self.moveCard('', piece, Pos.E_CEMETERY, 0)
                                
                                self.catched[1] += 1
                                target.getPiece()
                            
                            obj.addPiece(self.buffer.getPiece()) # type: ignore

                    self.accessable = []
                    self.buffer = None
                    self.state = State.NONE
