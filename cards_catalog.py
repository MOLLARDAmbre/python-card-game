from action import Action, TrapAction, SelectCardTrapAction
from events import Event, EventHandler
from card import Card

def draw_cards_gain_points(nb_cards, nb_points):
    def f(game):
        for _ in range(nb_cards):
            game.player_draw()
        game.add_points_player(nb_points)
    return f

def draw_cards(nb):
    def f(game):
        for _ in range(nb):
            game.player_draw()
    return f

def tap_card_free(game):
    EventHandler.get_instance().use_event(Event.START_SELECTION)
    def callback():
        card = game.display_manager.selected_card
        if card.middle_card:
            game.middle_cards_tapped -= 1  # Compensate the tapping
        card.tap()
    EventHandler.get_instance().add_event_listener_once(Event.END_SELECTION, callback)

def tap_to(to_exec):
    def f(game):
        game.display_manager.start_selection(lambda card: card.tappable and not
                card.tapped)
        def callback():
            card = game.display_manager.selected_card
            card.tap()
        EventHandler.get_instance().add_event_listener_once(Event.END_SELECTION, callback)
        to_exec(game)
    return f

def block_card(game):
    EventHandler.get_instance().use_event(Event.START_SELECTION)
    def callback():
        card = game.display_manager.selected_card
        card.block(game.display_manager.player)
    EventHandler.get_instance().add_event_listener_once(Event.END_SELECTION, callback)

def unblock_card(game):
    EventHandler.get_instance().use_event(Event.START_SELECTION)
    def callback():
        card = game.display_manager.selected_card
        card.unblock()
    EventHandler.get_instance().add_event_listener_once(Event.END_SELECTION, callback)

def protect_card(game):
    EventHandler.get_instance().use_event(Event.START_SELECTION)
    def callback():
        card = game.display_manager.selected_card
        card.protect()
    EventHandler.get_instance().add_event_listener_once(Event.END_SELECTION, callback)

def untap_at_next_turn_end(game):
    EventHandler.get_instance().use_event(Event.START_SELECTION)
    def callback():
        card = game.display_manager.selected_card
        EventHandler.get_instance().add_event_listener_once(Event.TURN_END, (lambda : EventHandler.get_instance().add_event_listener_once(Event.TURN_END, card.untap)))
    EventHandler.get_instance().add_event_listener_once(Event.END_SELECTION, callback)

def draw_one_gain_five_generator(card):
    def callback(game):
        if (card.tapped):
            game.player_draw()
            game.add_points_player(5)
            return True
        return False
    return callback

def check_untapped(card):
    def callback(game):
        if card.tapped:
            return False
        return True
    return callback

def neutral_crystal():
    name = "Neutral crystal"
    flavor_text = "As fragile as powerful, \nHolds the power of growth"
    img_path = "assets/4_pink.png"
    draw_action = Action("Draw two cards", draw_cards(2), tap_parent=True)
    draw_gain_action = Action("Draw a card and gain 5 points",
            draw_cards_gain_points(1, 5), tap_parent=True)
    gain_action = Action("Gain 10 points", draw_cards_gain_points(0, 10),
            tap_parent=True)
    blocked_action = Action("Do nothing", tap_parent=True,
    cond_description="Blocked")
    blocked_action.condition = (lambda game, player :
            blocked_action.parent.blocked and blocked_action.parent.blocked_player != player)
    actions = [draw_action, draw_gain_action, gain_action, blocked_action]
    return Card(name, actions, img_path, flavor_text=flavor_text,
            tappable=True, middle_card=True)

def neutral_crystal_maiden():
    name = "Neutral Maiden"
    flavor_text = "She likes her simple life attending to the crystal"
    img_path = "assets/11.png"
    draw_action = Action("Draw a card", draw_cards(1), lambda game : not game.check_activated(0))
    set_permanent_action = Action("Play as permanent", lambda game :
            game.add_player_permanent(neutral_crystal_maiden_permanent()),
            lambda game, player=None : game.check_activated(0), cond_description="Crystal activated")
    actions = [draw_action, set_permanent_action]
    return Card(name, actions, img_path, flavor_text=flavor_text)

def neutral_crystal_maiden_permanent():
    name = "Neutral Maiden"
    flavor_text = "She likes her simple life attending to the crystal"
    img_path = "assets/11.png"
    permanent_action = Action("Draw a card", draw_cards(1), tap_parent=True)
    actions = [permanent_action]
    return Card(name, actions, img_path, flavor_text=flavor_text)

def fire_crystal():
    name = "Fire crystal"
    flavor_text = "As fragile as powerful, \nHolds the power of destruction and healing"
    img_path = "assets/4_yellow.png"
    block_action = Action("Block a card for one turn", block_card,
            tap_parent=True)
    unblock_action = Action("Unblock a card", unblock_card, tap_parent=True)
    protect_action = Action("Protects a card aginst block",
            protect_card, tap_parent=True)
    blocked_action = Action("Tap this", tap_parent=True,
    cond_description="Blocked")
    blocked_action.condition = (lambda game, player : blocked_action.parent.blocked and
    blocked_action.parent.blocked_player != player)
    actions = [block_action, unblock_action, protect_action, blocked_action]
    return Card(name, actions, img_path, flavor_text=flavor_text,
            tappable=True, middle_card=True)

def fire_crystal_maiden():
    name = "Fire Maiden"
    flavor_text = "Her life with the crystal broke her soul\nShe now wanders around setting towns on fire"
    img_path = "assets/12.png"
    tap_action = Action("Tap a card", tap_card_free, lambda game, player=None : not game.check_activated(1))
    set_permanent_action = Action("Play as permanent", lambda game :
            game.add_player_permanent(fire_crystal_maiden_permanent()), lambda
            game, player=None : game.check_activated(1), cond_description="Crystal activated")
    actions = [tap_action, set_permanent_action]
    return Card(name, actions, img_path, flavor_text=flavor_text)

def fire_crystal_maiden_permanent():
    name = "Fire Maiden"
    flavor_text = "Her life with the crystal broke her soul\nShe now wanders around setting towns on fire"
    img_path = "assets/12.png"
    permanent_action = Action("Block a card", block_card, tap_parent=True)
    actions = [permanent_action]
    return Card(name, actions, img_path, flavor_text=flavor_text)

def water_crystal_maiden():
    name = "Water maiden"
    flavor_text = "She is sometimes seen underwater\nSailors tell tales of her fury sweeping them away"
    img_path = "assets/13.png"
    trap_action = SelectCardTrapAction("Trap a card : draw a card and gain 5 pts", draw_one_gain_five_generator, check_untapped)
    trap_action.condition = lambda game : not game.check_activated(2)
    set_permanent_action = Action("Play as permanent", lambda game :
            game.add_player_permanent(water_crystal_maiden_permanent()), lambda
            game : game.check_activated(2), cond_description="Crystal activated")
    actions = [trap_action, set_permanent_action]
    return Card(name, actions, img_path, flavor_text=flavor_text)

def water_crystal_maiden_permanent():
    name = "Water maiden"
    flavor_text = "She is sometimes seen underwater\nSailors tell tales of her fury sweeping them away"
    img_path = "assets/13.png"
    trap_action = SelectCardTrapAction("Trap a card : draw a card and gain 5 pts", draw_one_gain_five_generator, check_untapped, tap_parent=True)
    actions = [trap_action]
    return Card(name, actions, img_path, flavor_text=flavor_text)

def earth_crystal_maiden():
    name = "Earth Maiden"
    flavor_text = "She used to venerate the crystal.\nNow she IS part of the crystal.\nShe is said to bloom in Spring"
    img_path = "assets/14.png"
    tap_action = Action("Untap a card at the end of next turn",
            untap_at_next_turn_end, lambda game, player=None : not game.check_activated(3))
    set_permanent_action = Action("Play as permanent", lambda game :
            game.add_player_permanent(earth_crystal_maiden_permanent()), lambda
            game, player=None : game.check_activated(3), cond_description="Crystal activated")
    actions = [tap_action, set_permanent_action]
    return Card(name, actions, img_path, flavor_text=flavor_text)

def earth_crystal_maiden_permanent():
    name = "Earth Maiden"
    flavor_text = "She used to venerate the crystal.\nNow she IS part of the crystal.\nShe is said to bloom in Spring"
    img_path = "assets/14.png"
    permanent_action = Action("Untap a card at the end of next turn", untap_at_next_turn_end, tap_parent=True)
    actions = [permanent_action]
    return Card(name, actions, img_path, flavor_text=flavor_text)


def test_card():
    name = "Test"
    img_path = "assets/15.png"
    actions = [Action("Tap a card to gain 5 points", target=tap_to(lambda game: game.add_points_player(5)))]
    return Card(name, actions, img_path)
