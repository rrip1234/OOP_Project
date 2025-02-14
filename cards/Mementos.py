from CardList import *
from classes.Coroutine import waitForSeconds

name = '유품 회수'
short = 'mementos'
cost = 1
script = '묘지에서 직위 카드 두 장을 덱에 넣고, 덱을 섞는다. 한 장 드로우한다.'
subscript = ''

def precon(gm: GameManager):
    return len(gm.field_pos[Pos.P_CEMETERY].cards) > 1

def abillity(gm: GameManager, self_card: CardObject):
    condition = lambda obj: isinstance(obj, CardObject) and\
                            gm.isExist(Pos.P_CEMETERY, obj) and\
                            isinstance(obj.card_info, RoleCard)
    
    request = Request(condition, "묘지에서 직위 카드 두 장을 선택해주세요.", 2)

    cards = yield from gm.collector.sendRequest(request)

    gm.moveCard(cards[0], Pos.P_CEMETERY, Pos.P_DECK, 0.1)
    gm.moveCard(cards[1], Pos.P_CEMETERY, Pos.P_DECK, 0.1)
    gm.field_pos[Pos.P_DECK].shuffle()

    yield from waitForSeconds(0.5)

    gm.moveCard(0, Pos.P_DECK, Pos.P_HAND, 0.3, pytweening.easeInOutBack)

    yield from waitForSeconds(0.5)

    gm.moveCard(self_card, Pos.P_HAND, Pos.P_CEMETERY, 0)
    gm.state = State.NONE
    

AddCard(name, short, cost, script, subscript, abillity, precon)