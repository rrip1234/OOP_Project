from CardList import *

name = '한 번의 기회'
short = "chance"
cost = 1
script = '묘지에서 직위 카드 한 장을 회수한다.'
subscript = ''

def precon(gm: GameManager):
    return len(gm.field_pos[Pos.P_CEMETERY].cards) > 0

def abillity(gm: GameManager, self_card: CardObject):
    condition = lambda obj: isinstance(obj, CardObject) and\
                            gm.isExist(Pos.P_CEMETERY, obj) and\
                            isinstance(obj.base, RoleCard)
    
    request = Request(condition, "묘지에서 직위 카드 한 장을 선택해주세요.", 1)

    cards = yield from gm.collector.sendRequest(request)

    gm.moveCard(cards[0], Pos.P_CEMETERY, Pos.P_HAND, 0.3, pytweening.easeOutBack)

    yield from waitForSeconds(0.5)

    gm.moveCard(self_card, Pos.P_HAND, Pos.P_CEMETERY, 0)
    gm.state = State.NONE
    
AddCard(name, short, cost, script, subscript, abillity=abillity, precon=precon)