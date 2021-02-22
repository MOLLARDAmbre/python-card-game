import pygame
import constants
from events import EventHandler, Event
from math import sqrt
from action import Action
from action_selector import ActionSelector
from logger import Logger

class DisplayManager():
    # TODO add player hand, add opponent hand, add permanents row, add monsters row
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)
        self.display = pygame.display.set_mode((constants.WIDTH + constants.CARD_DISPLAY_WIDTH, constants.HEIGHT))
        self.game_display = pygame.Surface((constants.WIDTH, constants.HEIGHT))
        self.game_display.fill(constants.BG_COLOR)
        self.card_display = pygame.Surface((constants.CARD_DISPLAY_WIDTH, constants.HEIGHT))
        self.selected_card = None
        self.mode_selection = False
        self.controls_enabled = True
        self.select_callback = None
        self.player = game.player_id
        self.cards_pos = []  # Contains the card position (to make them clickable)
        self.cards = []  # Links the card position to the actual card
        self.cards_rows = []  # We define 5 rows of cards, and store in which row they are as that will help us move the cursor
        for card_nb in range(len(self.game.middle_cards)):
            position_rect = self.draw_card(self.game.middle_cards[card_nb], [(constants.CARD_X_MARGIN + card_nb * (constants.CARD_SPACING + constants.CARD_WIDTH) + int(constants.CARD_WIDTH / 2)) / constants.WIDTH, 0.5])
            self.cards.append(self.game.middle_cards[card_nb])
            self.cards_pos.append(position_rect)
            self.cards_rows.append(2)
        self.cursor_position = self.cards_pos[0]
        self.cursor_row = 2
        self.cursor_index = 0
        self.draw_cursor()
        self.action_selector = None
        ev_handler = EventHandler.get_instance()
        ev_handler.add_event_listener(Event.MOVE_LEFT, lambda : self.handle_left_press())
        ev_handler.add_event_listener(Event.MOVE_RIGHT, lambda : self.handle_right_press())
        ev_handler.add_event_listener(Event.MOVE_UP, lambda : self.handle_up_press())
        ev_handler.add_event_listener(Event.MOVE_DOWN, lambda : self.handle_down_press())
        ev_handler.add_event_listener(Event.VALID, lambda : self.handle_valid())
        ev_handler.add_event_listener(Event.START_SELECTION, lambda : self.start_selection())

    def update(self):
        """
        Updates the display and redraws everything.
        If we need more power, we can optimise that by adding a variable checking for everything that changed and only change those
        """
        self.game_display.fill(constants.BG_COLOR)
        self.cards = []
        self.cards_pos = []
        self.cards_rows = []
        for card_nb in range(len(self.game.middle_cards)):
            new_rect = self.draw_card(self.game.middle_cards[card_nb], [(constants.CARD_X_MARGIN + card_nb * (constants.CARD_SPACING + constants.CARD_WIDTH) + int(constants.CARD_WIDTH / 2)) / constants.WIDTH, 0.4])
            self.cards_pos.append(new_rect)
            self.cards_rows.append(2)
            self.cards.append(self.game.middle_cards[card_nb])
        for card_nb in range(len(self.game.player_permanents)):  # For now we will hard cap the permanents size at 5
            new_rect = self.draw_card(self.game.player_permanents[card_nb], [(constants.CARD_X_MARGIN + card_nb * (constants.CARD_SPACING + constants.CARD_WIDTH) + int(constants.CARD_WIDTH / 2)) / constants.WIDTH, 1 - 2 * constants.CARD_HEIGHT / constants.HEIGHT])
            self.cards_pos.append(new_rect)
            self.cards_rows.append(4)
            self.cards.append(self.game.player_permanents[card_nb])
        for card_nb in range(len(self.game.player_hand)):  # For now we will hard cap the hand size at 5
            new_rect = self.draw_card(self.game.player_hand[card_nb], [(constants.CARD_X_MARGIN + card_nb * (constants.CARD_SPACING + constants.CARD_WIDTH) + int(constants.CARD_WIDTH / 2)) / constants.WIDTH, 1 - 0.8 * constants.CARD_HEIGHT / constants.HEIGHT])
            self.cards_pos.append(new_rect)
            self.cards_rows.append(5)
            self.cards.append(self.game.player_hand[card_nb])

        self.cursor_index = self.find_best_cursor_next_position()
        self.cursor_position = self.cards_pos[self.cursor_index]
        self.cursor_row = self.cards_rows[self.cursor_index]
        self.draw_cursor()
        self.draw_points(self.game.player_points)
        self.draw_all_cristal_icons()

        if self.action_selector != None:
            self.action_selector.draw(self.game_display)
            self.action_selector.actions_enabled = True
        if self.mode_selection:
            self.draw_select_indicator()
        self.display.blit(self.cards[self.cursor_index].draw_big(self.card_display, self.font, (0, 0, constants.CARD_DISPLAY_WIDTH, constants.HEIGHT)), (0, 0))
        self.display.blit(self.game_display, (constants.CARD_DISPLAY_WIDTH, 0))

    def enable_controls(self):
        self.controls_enabled = True
        Logger.get_instance().decrease_identation()
        Logger.get_instance().log_info("Enabled controls for ui")

    def disable_controls(self):
        self.controls_enabled = False
        Logger.get_instance().log_info("Disabled controls for ui")
        Logger.get_instance().increase_identation()

    def find_best_cursor_next_position(self):
        same_row = []
        other_row = []
        dists = []
        for card_id in range(len(self.cards)):
            if self.cards_rows[card_id] == self.cursor_row:
                same_row.append(card_id)
                dists.append(self.distance(self.cards_pos[card_id], self.cursor_position))
        if len(same_row) != 0:
            closest = self.get_closest(dists)
            return same_row[closest]
        for card_id in range(len(self.cards)):
            other_row.append(card_id)
            dists.append(self.distance(self.cards_pos[card_id], self.cursor_position))
        closest = self.get_closest(dists)
        return other_row[closest]

    def draw_select_indicator(self):
        text_render = self.font.render("Selection mode", True, constants.CURSOR_COLOR)
        self.game_display.blit(text_render, (constants.WIDTH - 3 * int(constants.CARD_WIDTH), constants.CARD_SPACING))


    def draw_points(self, nb_points):
        rect = pygame.Surface((constants.POINTS_MARQUER_SIZE, constants.POINTS_MARQUER_SIZE))
        rect.fill(constants.BG_COLOR)
        rect.set_colorkey(constants.BG_COLOR)
        pygame.draw.rect(rect, constants.BLACK, (0, 0, constants.POINTS_MARQUER_SIZE, constants.POINTS_MARQUER_SIZE))
        pygame.draw.rect(rect, constants.CURSOR_COLOR, (constants.POINTS_MARQUER_SIZE * 0.1 - 2, constants.POINTS_MARQUER_SIZE * 0.1 - 2, constants.POINTS_MARQUER_SIZE * 0.8, 3))
        pygame.draw.rect(rect, constants.CURSOR_COLOR, (constants.POINTS_MARQUER_SIZE * 0.1 - 2, constants.POINTS_MARQUER_SIZE * 0.1 - 2, 3, constants.POINTS_MARQUER_SIZE * 0.8))
        pygame.draw.rect(rect, constants.CURSOR_COLOR, (constants.POINTS_MARQUER_SIZE * 0.9 - 2, constants.POINTS_MARQUER_SIZE * 0.1 - 2, 3, constants.POINTS_MARQUER_SIZE * 0.85))
        pygame.draw.rect(rect, constants.CURSOR_COLOR, (constants.POINTS_MARQUER_SIZE * 0.1 - 2, constants.POINTS_MARQUER_SIZE * 0.9 - 2, constants.POINTS_MARQUER_SIZE * 0.8, 3))
        rect = pygame.transform.rotate(rect, 45)
        self.game_display.blit(rect, (constants.CARD_SPACING, constants.CARD_SPACING))
        text_render = self.font.render(str(nb_points), True, constants.BG_COLOR)
        self.game_display.blit(text_render, (constants.CARD_SPACING + int(constants.POINTS_MARQUER_SIZE * 0.65), constants.CARD_SPACING + int(constants.POINTS_MARQUER_SIZE * 0.6)))

    def draw_cristal_icon(self, rect, col):
        left, top, width, height = rect
        diamond = pygame.Surface((width, height))
        diamond.fill(constants.BG_COLOR)
        diamond.set_colorkey(constants.BG_COLOR)
        pygame.draw.rect(diamond, col, (0, 0, width, height))
        diamond = pygame.transform.rotate(diamond, 45)
        self.game_display.blit(diamond, (left, top))

    def draw_cristal_valid(self, rect, col):
        left, top, width, height = rect
        new_rect = (left + int(width / 3) + 3, top + int(height / 3) + 3, int(width / 3), int(height / 3))
        col = constants.BG_COLOR
        pygame.draw.rect(self.game_display, col, new_rect)
        return

    def draw_all_cristal_icons(self):
        rects = []
        for icon_nb in range(5):
            icon_index = self.game.player_objectives[icon_nb]
            icon_activated = self.game.player_activated[icon_nb]
            col = constants.get_middle_color(icon_index)
            rect = (int(constants.CARD_X_MARGIN / 2), constants.HEIGHT - int((constants.CARD_HEIGHT / 3) * (icon_nb + 2)), int(constants.CARD_WIDTH / 5), int(constants.CARD_HEIGHT / 5))
            self.draw_cristal_icon(rect, col)
            rects.append(rect)
            if icon_activated:
                self.draw_cristal_valid(rect, col)
        return rects

    def draw_card(self, card, pos):
        """
        Displays a card on the ui
        :params card: Card to display
        :params pos: [x, y] position to display the card at, between 0 and 1
        :return: rect that was draw on
        """
        left = int(constants.WIDTH * pos[0] - constants.CARD_WIDTH / 2)
        width = constants.CARD_WIDTH
        top = int(constants.HEIGHT * pos[1] - constants.CARD_HEIGHT / 2)
        height = constants.CARD_HEIGHT
        (left, top, width, height) = card.draw(self.game_display, (left, top, width, height))  # Will be called for the card to draw itself when implemented
        return (left, top, width, height)

    def draw_cursor(self):
        """
        Displays the cursor which is used to select cards through the keyboard
        """
        left, top, width, height = self.cursor_position
        rects = [
        (int(left - constants.WIDTH * 0.02), int(top - constants.HEIGHT * 0.02), int(width + constants.WIDTH * 0.04), int(constants.HEIGHT * 0.02)),
        (int(left - constants.WIDTH * 0.02), int(top + height), int(width + constants.WIDTH * 0.04), int(constants.HEIGHT * 0.02)),
        (int(left - constants.WIDTH * 0.02), int(top - constants.HEIGHT * 0.02), int(constants.WIDTH * 0.02), int(height + constants.HEIGHT * 0.02)),
        (int(left + width), int(top - constants.HEIGHT * 0.02), int(constants.WIDTH * 0.02), int(height + constants.HEIGHT * 0.02))
        ]
        for rect in rects:
            pygame.draw.rect(self.game_display, constants.CURSOR_COLOR, rect)
        self.draw_cursor_part_hor(rects[0])
        self.draw_cursor_part_hor(rects[1])
        self.draw_cursor_part_vert(rects[2])
        self.draw_cursor_part_vert(rects[3])

    def draw_cursor_part_vert(self, cursor_rect):
        left, top, width, height = cursor_rect
        bg_rect = (left + width / 2 - 1, top + constants.WIDTH * 0.01, 2, height - constants.CARD_HEIGHT * 0.02)
        mix_rect_left = (bg_rect[0] - 2, bg_rect[1], bg_rect[2], bg_rect[3])
        mix_rect_right = (bg_rect[0] + 2, bg_rect[1], bg_rect[2], bg_rect[3])
        mix_color = [int((constants.BG_COLOR[i] + constants.CURSOR_COLOR[i]) / 2) for i in range(3)]
        pygame.draw.rect(self.game_display, constants.BG_COLOR, bg_rect)
        pygame.draw.rect(self.game_display, mix_color, mix_rect_left)
        pygame.draw.rect(self.game_display, mix_color, mix_rect_right)

    def draw_cursor_part_hor(self, cursor_rect):
        left, top, width, height = cursor_rect
        bg_rect = (left + constants.HEIGHT * 0.01 - 1, top + height / 2, width - constants.HEIGHT * 0.015, 2)
        mix_rect_left = (bg_rect[0], bg_rect[1] - 2, bg_rect[2], bg_rect[3])
        mix_rect_right = (bg_rect[0] , bg_rect[1] + 2, bg_rect[2], bg_rect[3])
        mix_color = [int((constants.BG_COLOR[i] + constants.CURSOR_COLOR[i]) / 2) for i in range(3)]
        pygame.draw.rect(self.game_display, constants.BG_COLOR, bg_rect)
        pygame.draw.rect(self.game_display, mix_color, mix_rect_left)
        pygame.draw.rect(self.game_display, mix_color, mix_rect_right)

    def distance(self, a, b):
        """
        Returns the euclidian distance between points a and b
        :params a: [x, y] values
        :params b: [x, y] values
        """
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def get_closest(self, distances):
        min_dist, index = -1, -1
        for card_index in range(len(distances)):
            dist = distances[card_index]
            if min_dist < 0 or min_dist > dist:
                min_dist = dist
                index = card_index
        return index

    def get_farthest(self, distances):
        max_dist, index = -1, -1
        for card_index in range(len(distances)):
            dist = distances[card_index]
            if max_dist < 0 or max_dist < dist:
                max_dist = dist
                index = card_index
        return index

    def get_cards_left(self):
        cards_left = []
        cards_dist = []
        for card_id in range(len(self.cards)):
            if self.cards_rows[card_id] == self.cursor_row:
                if self.cards_pos[card_id][0] < self.cursor_position[0]:
                    cards_left.append(card_id)
                    cards_dist.append(self.distance(self.cursor_position, self.cards_pos[card_id]))
        return cards_left, cards_dist

    def get_cards_right(self):
        cards_right = []
        cards_dist = []
        for card_id in range(len(self.cards)):
            if self.cards_rows[card_id] == self.cursor_row:
                if self.cards_pos[card_id][0] > self.cursor_position[0]:
                    cards_right.append(card_id)
                    cards_dist.append(self.distance(self.cursor_position, self.cards_pos[card_id]))
        return cards_right, cards_dist

    def get_max_from_list(self, l):
        if len(l) == 1:
            return l[0]
        return self.get_max_from_list([max(l[0], l[1])] + l[2:])

    def get_cards_up(self):
        cards_up = []
        cards_dist = []
        for card_id in range(len(self.cards)):
            if self.cards_rows[card_id] < self.cursor_row:
                cards_up.append(card_id)
        if len(cards_up) == 0:
            return cards_up, cards_dist, 0
        search_row = self.get_max_from_list([self.cards_rows[i] for i in cards_up])
        cards_up = []
        for card_id in range(len(self.cards)):
            if self.cards_rows[card_id] == search_row:
                cards_up.append(card_id)
                cards_dist.append(self.distance(self.cursor_position, self.cards_pos[card_id]))
        return cards_up, cards_dist, search_row

    def get_min_from_list(self, l):
        if len(l) == 1:
            return l[0]
        return self.get_min_from_list([min(l[0], l[1])] + l[2:])

    def get_cards_down(self):
        cards_down = []
        cards_dist = []
        for card_id in range(len(self.cards)):
            if self.cards_rows[card_id] > self.cursor_row:
                cards_down.append(card_id)
        if len(cards_down) == 0:
            return cards_down, cards_dist, 0
        search_row = self.get_min_from_list([self.cards_rows[i] for i in cards_down])
        cards_down = []
        for card_id in range(len(self.cards)):
            if self.cards_rows[card_id] == search_row:
                cards_down.append(card_id)
                cards_dist.append(self.distance(self.cursor_position, self.cards_pos[card_id]))
        return cards_down, cards_dist, search_row

    def handle_left_press(self):
        if not self.controls_enabled:
            return
        cards_left, cards_dist = self.get_cards_left()
        if len(cards_left) == 0:
            cards_right, cards_dist = self.get_cards_right()
            if len(cards_right) == 0:
                return  # The card is alone in its row, return
            farthest = cards_right[self.get_farthest(cards_dist)]
            self.cursor_position = self.cards_pos[farthest]
            self.cursor_index = farthest
        else:
            closest = cards_left[self.get_closest(cards_dist)]
            self.cursor_position = self.cards_pos[closest]
            self.cursor_index = closest

    def handle_right_press(self):
        if not self.controls_enabled:
            return
        cards_right, cards_dist = self.get_cards_right()
        if len(cards_right) == 0:
            cards_left, cards_dist = self.get_cards_left()
            if len(cards_left) == 0:
                return  # This card is alone in its row, return
            farthest = cards_left[self.get_farthest(cards_dist)]
            self.cursor_position = self.cards_pos[farthest]
            self.cursor_index = farthest
        else:
            closest = cards_right[self.get_closest(cards_dist)]
            self.cursor_position = self.cards_pos[closest]
            self.cursor_index = closest

    def handle_up_press(self):
        if not self.controls_enabled:
            return
        cards_up, cards_dist, row = self.get_cards_up()
        if len(cards_up) == 0:
            return
        else:
            closest = cards_up[self.get_closest(cards_dist)]
            self.cursor_position = self.cards_pos[closest]
            self.cursor_index = closest
            self.cursor_row = row

    def handle_down_press(self):
        if not self.controls_enabled:
            return
        cards_down, cards_dist, row = self.get_cards_down()
        if len(cards_down) == 0:
            return
        else:
            closest = cards_down[self.get_closest(cards_dist)]
            self.cursor_position = self.cards_pos[closest]
            self.cursor_index = closest
            self.cursor_row = row

    def handle_valid(self):
        if not self.controls_enabled:
            return
        for card_id in range(len(self.cards)):
            if self.cursor_position == self.cards_pos[card_id]:
                selected_card = self.cards[card_id]
                selected_rect = self.cards_pos[card_id]
        self.select_action(selected_card, selected_rect)

    def select_action(self, card, card_pos):
        if self.mode_selection:
            if self.select_callback(card):
                action_list = [Action(description="Select", target=lambda _ : self.finish_selection(card))]
            else:
                action_list = []
        else:
            action_list = card.get_actions_list(self.game, self.player)
            if self.cursor_row == 5:  # The card is currently in the hand
                for action in action_list:
                    action.from_hand = True
        action_cancel = Action(description="Cancel", target=lambda _ : None, true_action=False)
        action_list.append(action_cancel)
        action_inspect = Action(description="Debug", target=lambda _ : card.inspect())
        action_list.append(action_inspect)
        left, top, width, height = card_pos
        given_rect = (left - width * 0.3, top + height * 0.2, constants.ACTION_SELECTOR_WIDTH, constants.ACTION_SELECTOR_HEIGHT * len(action_list))
        self.action_selector = ActionSelector(self, action_list, given_rect)
        self.disable_controls()

    def start_selection(self, callback=None):
        """
        Enters selection mode
        """
        if callback == None:
            callback = lambda card, player=self.player : card.can_be_tapped(player)
        self.mode_selection = True
        self.select_callback = callback

    def finish_selection(self, card):
        """
        Exit selection mode
        """
        self.selected_card = card
        self.mode_selection = False
        self.select_callback = None
        EventHandler.get_instance().use_event(Event.END_SELECTION)

    def close_selector(self, action):
        self.action_selector = None
        self.enable_controls()
        action.run(self.game)
