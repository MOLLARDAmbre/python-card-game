from events import *
from logger import Logger
from card import Card

class Action():
    """
    Represents an action to be played, with a description, what to do and when it is available
    """
    def __init__(self, description="Description", target=(lambda board_state,
        player=None : None), condition=(lambda board_state, player=None : True), cond_description="", tap_parent=False, true_action=True):
        self.description = description
        self.target = target
        self.condition = condition
        self.parent = None
        self.tap = tap_parent  # Whether the parent should be tapped
        self.condition_descr = cond_description
        if self.tap:
            def check_condition(game, player=None):
                return self.parent.can_be_tapped(player) and condition(game, player)
            self.condition = check_condition
        self.true_action = true_action  # Checks whether the action is there to display or to be used
        if self.tap:
            self.description = "TAP : " + self.description  # Make things more clear on which card to tap
        self.from_hand = False  # If the card is played from the hand, send a signal to the card, so that it can be removed properly

    def available(self, board_state, player=None):
        try:
            return (self.condition)(board_state, player)
        except:
            return (self.condition)(board_state)

    def run(self, board_state, player=None):
        """
        Runs the actions effect
        """
        if self.true_action:
            Logger.get_instance().log_action(self.description)
            EventHandler.get_instance().use_event(Event.CARD_USED)
        if self.tap:
            self.parent.tap()
        if self.from_hand:
            self.parent.on_play(board_state)
        try:
            (self.target)(board_state, parent)
        except:
            (self.target)(board_state)


class TrapAction(Action):
    """
    Action used to trap an opponent action
    You will need to have an effect to activate and an event to listen to
    """
    def __init__(self, description="Description", activate_trap=(lambda board_state : None), listen_to=Event.TEST, tap_parent=False):
        super().__init__(description, target=self.setup, condition=(lambda _ : not self.is_setup), tap_parent=tap_parent)
        self.listen_to = listen_to
        self.activate_trap = activate_trap
        self.listener = None  # Stored listener for cleaning up
        self.remove_from_permanent_listener = None  # Stored listeners for cleaning up
        self.is_setup = False  # Allows to display what has been trapped while locking the action

    def setup(self, game_state):
        self.true_action = False
        self.parent.actions = [self]  # No other action can be used now
        self.is_setup = True  # This is no longer available
        self.listener = lambda game=game_state : self.trigger(game_state)
        self.listener_setup = lambda : EventHandler.get_instance().add_event_listener(self.listen_to, self.listener)
        game_state.add_player_permanent(self.parent)  # Make the card here for the player to check
        self.remove_from_permanent_listener = lambda game=game_state, parent=self.parent : self.remove_from_permanents(game, parent)
        self.parent.actions.append(Action("TRAP : " + self.description))  # Just to show the text
        ev_handler = EventHandler.get_instance()
        ev_handler.add_event_listener(Event.TURN_END, self.listener_setup)
        ev_handler.add_event_listener(Event.TURN_END, self.remove_from_permanent_listener)
        ev_handler.add_event_listener(Event.TURN_END, lambda : ev_handler.remove_event_listener(Event.TURN_END, self.remove_from_permanent_listener))
        ev_handler.add_event_listener(Event.TURN_END, lambda : ev_handler.remove_event_listener(Event.TURN_END, self.listener_setup))

    def remove_from_permanents(self, game_state, card):
        game_state.player_permanents.remove(card)

    def trigger(self, game_state):
        Logger.get_instance().log_action("TRAP succeded : " + self.description)
        (self.activate_trap)(game_state)
        # EventHandler.get_instance().remove_event_listener(self.listen_to, self.listener)

class SelectCardTrapAction(TrapAction):
    def __init__(self, description="Description", activate_trap_generator=(lambda var : (lambda game : None)), check=(lambda var : (lambda game : True)), tap_parent=False, parent=None):
        super().__init__(description, lambda game : None, Event.CARD_TAPPED, tap_parent=tap_parent)
        self.generator = activate_trap_generator
        self.check = check
        self.prepared_check = None
        self.tap_parent = tap_parent
        self.parent = parent
        self.trap_display = None
        if parent != None:
            self.parent.actions.append(self)

    def reset(self):
        self.parent.reset_actions()
        self.parent.actions.remove(self)
        new_action = SelectCardTrapAction(self.description[6:], self.generator, self.check, tap_parent=self.tap_parent, parent=self.parent)

    def available(self, game, player=None):
        return not self.is_setup

    def setup(self, game):
        EventHandler.get_instance().use_event(Event.START_SELECTION)
        def callback():
            card = game.display_manager.selected_card
            self.trap_display = Card(name="Trap", image_path=self.parent.image_path, actions=[Action(self.description, true_action=False)])
            self.prepared_check = self.check(card)
            self.activate_trap = self.generator(card)
            self.true_action = False
            self.parent.actions = [self]  # No other action can be used now
            self.is_setup = True  # This is no longer available
            self.check_listener = lambda game=game : self.handle_checks(game)
            self.listener = lambda game=game : self.trigger(game)
            self.listener_setup = lambda : EventHandler.get_instance().add_event_listener(self.listen_to, self.listener)
            game.add_player_permanent(self.trap_display)  # Make the card here for the player to check
            self.remove_from_permanent_listener = lambda game=game : self.remove_from_permanents(game, self.trap_display)
            self.parent.actions.append(Action("TRAP : " + self.description))  # Just to show the text
            if self.tap_parent:
                self.parent.tap()
            ev_handler = EventHandler.get_instance()
            ev_handler.add_event_listener(Event.TURN_END, self.check_listener)
            ev_handler.add_event_listener(Event.TURN_END, self.listener_setup)
            ev_handler.add_event_listener(Event.TURN_END, self.remove_from_permanent_listener)
            ev_handler.add_event_listener(Event.TURN_END, self.clean)
            ev_handler.remove_event_listener(Event.END_SELECTION, callback)
        EventHandler.get_instance().add_event_listener(Event.END_SELECTION, callback)

    def clean(self):
        EventHandler.get_instance().remove_event_listener(Event.TURN_END, self.remove_from_permanent_listener)
        EventHandler.get_instance().remove_event_listener(Event.TURN_END, self.clean)
        EventHandler.get_instance().remove_event_listener(Event.TURN_END, self.listener_setup)
        EventHandler.get_instance().remove_event_listener(Event.TURN_END, self.check_listener)

    def handle_checks(self, game):
        if self.prepared_check(game):
            return
        self.remove_from_permanent_listener()
        self.clean()


    def trigger(self, game_state):
        if (self.activate_trap)(game_state):
            Logger.get_instance().log_action("TRAP succeded : " + self.description)
            EventHandler.get_instance().remove_event_listener(self.listen_to, self.listener)
