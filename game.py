import card_loader
import cards_catalog
import random
import string
from card import Card
from ui import DisplayManager
from events import *
from ai import AI

class Game():
    def __init__(self):
        self.middle_cards = [cards_catalog.neutral_crystal(),
                cards_catalog.fire_crystal(), card_loader.stub_middle_card(2), card_loader.stub_middle_card(3), card_loader.stub_middle_card(4)]
        self.player_hand = []
        self.player_permanents = []
        self.opponent_cards = []
        self.player_id = ''.join([random.choice(string.ascii_lowercase) for _
            in range(10)])
        self.display_manager = DisplayManager(self)
        self.player_objectives = [0, 1, 2, 3, 4]
        random.shuffle(self.player_objectives)
        self.opponent_objectives = [0, 1, 2, 3, 4]
        random.shuffle(self.opponent_objectives)
        self.player_activated = [False, False, False, False, False]
        self.player_points = 0
        self.middle_cards_tapped = 0
        self.first_move = True
        self.player_turn = True  # Checks whether the player or ai will play
        self.ai = AI(self.opponent_objectives, self.player_objectives)
        self.first_turn = True  # First turn will have limitations
        self.end_turn = False
        ev_handler = EventHandler.get_instance()
        ev_handler.add_event_listener(Event.CARD_USED, lambda : self.card_used())
        ev_handler.add_event_listener(Event.TURN_END, lambda : self.new_turn())
        ev_handler.add_event_listener(Event.MIDDLE_CARD_TAPPED, lambda : self.add_middle_card_tapped())

        """
        Testing setups
        """
        self.player_draw(cards_catalog.neutral_crystal_maiden())
        self.player_draw(cards_catalog.fire_crystal_maiden())
        self.player_draw(cards_catalog.water_crystal_maiden())
        #self.player_draw(cards_catalog.earth_crystal_maiden())
        # self.player_draw(card_loader.trap_card_test())
        # self.player_draw(card_loader.tapper_test())
        # self.player_draw(card_loader.permanent_tap_draw_hand())
        # self.player_draw(card_loader.get_five_points())
        self.player_draw(cards_catalog.test_card())
        self.player_draw(card_loader.permanent_gain_points_hand())
        # self.add_player_monster(Card(), 3)
        # ev_handler.add_event_listener(Event.TEST, lambda : EventHandler.get_instance().use_event(Event.TURN_END))

    def update(self):
        if not self.player_turn:
            self.ai.play(self.middle_cards, [], [], [], self.player_permanents, [], self.player_activated)
        if not sum([not card.tapped for card in self.middle_cards]):  # All cards are tapped
            self.untap_all()
            self.end_turn = True
        self.display_manager.update()
        if sum(self.player_activated) == 5:  # All cards activated
            EventHandler.get_instance().use_event(Event.GAME_OVER)
        if self.end_turn:
            if not self.display_manager.mode_selection:
                EventHandler.get_instance().use_event(Event.TURN_END)

    def untap_all(self):
        for card in (self.player_monsters + self.player_permanents + self.middle_cards):
            try:
                card.untap()
            except:
                pass

    def add_points_player(self, nb_points):
        self.player_points += nb_points

    def add_middle_card_tapped(self):
        self.middle_cards_tapped += 1
        if self.middle_cards_tapped == 2:
            self.end_turn = True

    def card_used(self):
        self.first_move = False

    def new_turn(self):
        self.first_move = True
        self.middle_cards_tapped = 0
        self.player_turn = not self.player_turn
        self.end_turn = False
        self.first_turn = False

    def player_draw(self, new_card=None):
        if len(self.player_hand) >= 5:
            return  # Hard limit hand size to 5
        if new_card == None:
            new_card = Card(owner=self.player_id)
        else:
            new_card.owner = self.player_id
        self.player_hand.append(new_card)

    def add_player_permanent(self, permanent_card = None):
        if len(self.player_permanents) >= 5:
            return  # Hard limit to 5 for now
        if permanent_card == None:
            permanent_card = Card(owner=self.player_id)
        else:
            permanent_card.owner = self.player_id
        self.player_permanents.append(permanent_card)

    def activate(self, index):
        """
        Activates a middle card and make it count towards end goal
        """
        self.middle_cards[index].tap()
        next_obj = 0
        while self.player_activated[next_obj]:
            next_obj += 1
        if self.player_objectives[next_obj] == index:
            self.player_activated[next_obj] = True
            self.player_points -= [10, 10, 10, 20, 20][next_obj]
        self.end_turn = True

    def can_activate(self, index):
        next_obj = 0
        while self.player_activated[next_obj]:
            next_obj += 1
        points = [10, 10, 10, 20, 20][next_obj]
        return (self.player_objectives[next_obj] == index and self.player_points >= points)

    def check_activated(self, index):
        """
        This index refers to the pre-shuffled index
        """
        next_obj = 0
        while self.player_activated[next_obj]:
            if self.player_objectives[next_obj] == index:
                return True
            next_obj += 1
        return False
