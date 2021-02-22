from action import Action, TrapAction
from card import Card
from events import Event, EventHandler

def draw_1(game):
    game.player_draw()

def draw_2(game):
    game.player_draw()
    game.player_draw()

def tap_a_card(game):
    EventHandler.get_instance().use_event(Event.START_SELECTION)
    def callback():
        card = game.display_manager.selected_card
        card.tap()
        if card.middle_card:
            game.middle_cards_tapped -= 1  # Compensate the tapping
    EventHandler.get_instance().add_event_listener(Event.END_SELECTION, callback)

def tap_to(reward):
    def fun(game):
        EventHandler.get_instance().use_event(Event.START_SELECTION)
        def callback():
            card = game.display_manager.selected_card
            card.tap()
            reward(game)
        EventHandler.get_instance().add_event_listener(Event.END_SELECTION, callback)
    return fun

def middle_card0():
    name = "Middle Card 0"
    img_path = "assets/4_blue.png"
    draw_1_action = Action(description="Draw a card", target = draw_1, condition = (lambda game_state : True))
    draw_2_action = Action(description="Draw 2 cards", target = draw_2, tap_parent=True)
    draw_2_action.condition = (lambda game : not draw_2_action.parent.tapped)
    activate = Action(description="Activate this card", target=lambda game : game.activate(0))
    activate.condition = (lambda game : game.first_move and game.can_activate(0) and not activate.parent.tapped)
    action_list = [draw_1_action, draw_2_action, activate]
    return Card(name, action_list, img_path, tappable=True, middle_card=True, flavor_text="This is just a test")

def permanent_tap_draw_hand():
    name = "Tap to draw (hand)"
    img_path = "assets/7.png"
    action = Action(description="Play the card (TAP : draw 1)", target = (lambda game : game.add_player_permanent(permanent_tap_draw())))
    action_list = [action]
    return Card(name, action_list, img_path)

def permanent_tap_draw():
    name = "Tap to draw"
    img_path = "assets/7.png"
    action = Action(description="Draw a card", target=draw_1, tap_parent=True)
    return Card(name, [action], img_path, tappable=True)

def permanent_gain_points_hand():
    name = "Tap for points (hand)"
    img_path = "assets/10.png"
    action = Action(description="Play the card (TAP : gain 20)", target = (lambda game : game.add_player_permanent(permanent_gain_points())))
    action_list = [action]
    return Card(name, action_list, img_path)

def permanent_gain_points():
    name = "Tap for points"
    img_path = "assets/10.png"
    action = Action(description="Gain 20 points", target=(lambda game : game.add_points_player(20)), tap_parent=True)
    return Card(name, [action], img_path, tappable=True)

def get_five_points():
    name = "Get 5 points"
    img_path = "assets/8.png"
    action = Action(description="Gain 5 points", target=(lambda game : game.add_points_player(5)))
    tap_action = Action(description="Tap a card to gain 20 points", target = tap_to(lambda game : game.add_points_player(20)))
    return Card(name, [action, tap_action], img_path)

def stub_middle_card(i):
    name = "Middle card stub"
    if i == 1:
        img_path = "assets/4_yellow.png"
    if i == 2:
        img_path = "assets/4_pink.png"
    if i == 3:
        img_path = "assets/4_purple.png"
    if i == 4:
        img_path = "assets/4_green.png"
    activate = Action(description="Activate this card", target=lambda game, i=i : game.activate(i))
    activate.condition = (lambda game, i=i : game.first_move and game.can_activate(i) and not activate.parent.tapped)
    tap_action = Action(description="", target=lambda game : None, tap_parent=True)
    tap_action.condition = (lambda _ : not tap_action.parent.tapped)
    actions_list = [activate, tap_action]
    return Card(name, actions_list, img_path, tappable=True, middle_card=True)


def stub_card(im_path):
    name = f"Stub {im_path}"
    action_list = []
    return Card(name, action_list, im_path)

def trap_card_test():
    name = "Trap card"
    img_path = "assets/5.png"
    trap_draw_1_action = TrapAction(description="Draw a card when TEST", activate_trap=draw_1, listen_to=Event.TEST)
    trap_draw_2_action = TrapAction(description="Draw two card when TEST", activate_trap=draw_2, listen_to=Event.TEST)
    action_list = [trap_draw_1_action, trap_draw_2_action]
    return Card(name, action_list, img_path)

def tapper_test():
    name = "Tapper"
    img_path = "assets/6.png"
    tap_card_action = Action(description="Tap a card", target=tap_a_card)
    return Card(name, [tap_card_action], img_path)
