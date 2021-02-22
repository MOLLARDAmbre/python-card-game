def draw_1(game):
    game.player_draw()

def draw_2(game):
    game.player_draw()
    game.player_draw()

def select(game):
    EventHandler.get_instance().use_event(Event.START_SELECTION)
    def callback():
        card = game.display_manager.selected_card
        # Put code here
    EventHandler.get_instance().add_event_listener(Event.END_SELECTION, callback)

def tap_a_card(game):
    EventHandler.get_instance().use_event(Event.START_SELECTION)
    def callback():
        card = game.display_manager.selected_card
        card.tap()
        if card.middle_card:
            game.middle_cards_tapped -= 1  # Compensate the tapping
    EventHandler.get_instance().add_event_listener(Event.END_SELECTION, callback)
