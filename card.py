import pygame
import constants
from logger import Logger
from events import *

class Card():
    def __init__(self, name="placeholder", actions=[], image_path=None,
            owner=None, tappable=False, middle_card=False, flavor_text=None):
        self.name = name
        self.tapped = False
        self.tappable = tappable
        self.middle_card = middle_card
        self.actions = actions
        self.flavor_text = flavor_text
        self.actions_backup = actions
        self.image_path = image_path
        self.owner = owner
        self.blocked = False
        self.blocked_player = None
        for action in  self.actions:
            action.parent = self
        try:
            self.image = pygame.image.load(image_path)
            width, height = constants.CARD_WIDTH, constants.CARD_HEIGHT
            self.image = pygame.transform.scale(self.image, (int(min(width, height)), int(min(width, height))))
            self.tapped_image = pygame.transform.rotate(self.image, 90)
        except:
            self.image = None
            self.tapped_image = None
            Logger.get_instance().log_warning("Failed to load image " + str(image_path))

    def inspect(self):
        import pdb; pdb.set_trace()

    def run(board_state):
        """
        Activates the card, each card having a specific effect (this function will be overwritten)
        :params board_state: Game instance
        """
        pass

    def tap(self):
        if not self.tappable:
            Logger.get_instance().log_warning("Beware, untappable card tapped")
        self.tapped = True
        EventHandler.get_instance().use_event(Event.CARD_TAPPED)
        if self.middle_card:
            EventHandler.get_instance().use_event(Event.MIDDLE_CARD_TAPPED)

    def can_be_tapped(self, player=None):
        base_tap = self.tappable and not self.tapped
        if self.blocked and self.blocked_player != self.owner:
            return False
        if player == None or self.owner == None:
            return base_tap
        else:
            return base_tap and player==self.owner

    def untap(self):
        self.tapped = False
        for action in self.actions:
            try:
                action.reset()
                action.parent = self
            except:
                pass

    def reset_actions(self):
        self.actions = self.actions_backup

    def block(self, player):  # TODO
        self.blocked = True
        #pass
        # self.blocked = True
        # EventHandler.get_instance().add_event_listener(Event.TURN_END, self.unblock)

    def unblock(self):  # TODO also add one more step so that it actually works
        pass
        # self.blocked = False
        # EventHandler.get_instance().remove_event_listener(Event.TURN_END, self.unblock)

    def protect(self):  # Makes it impossible to block the card for one turn
        pass

    def get_actions_list(self, board_state, player):
        available_actions = []
        for action in self.actions:
            if action.available(board_state, player=player):
                available_actions.append(action)
        return available_actions

    def on_play(self, game):
        try:
            game.player_hand.remove(self)
        except:
            pass # Will be used later to remove from opponent hand
        return


    def draw(self, display, rect):
        """
        Draws the card. Should only draw inside the given rectangle
        :params display: The surface to draw on
        :params rect: The rectangle we are allowed to draw on
        :return: rect we actually drawn on
        """
        left, top, width, height = rect
        if (self.tapped):
            top += constants.HEIGHT * 0.01
            height -= constants.HEIGHT * 0.02
            im = self.tapped_image
        else:
            left += constants.WIDTH * 0.01
            width -= constants.WIDTH * 0.02
            im = self.image
        pygame.draw.rect(display, constants.BLACK, (left, top, width, height))
        if im != None:
            display.blit(im, (left, top))
        return (left, top, width, height)

    def draw_big(self, display, font, rect):
        """
        Draws a big version of the card with more details (including name and actions)
        """
        left = rect[0] + constants.CARD_DISPLAY_X_MARGIN
        top = rect[1] + constants.CARD_DISPLAY_Y_MARGIN
        width = rect[2] - 2 * constants.CARD_DISPLAY_X_MARGIN
        height = rect[3] - 2 * constants.CARD_DISPLAY_Y_MARGIN
        display.fill(constants.BG_COLOR)
        pygame.draw.rect(display, constants.BLACK, (left, top, width, height))
        pygame.draw.rect(display, constants.BG_COLOR, (left + 5, top + 0.07 * height, width - 10, 3))
        text_render = font.render(self.name, True, constants.BG_COLOR)
        display.blit(text_render, (left + 15, top + 15))
        if self.image != None:
            display.blit(pygame.transform.scale(self.image, (int(width * 0.5), int(width * 0.5))), (int(left + width * 0.22), int(top + 0.1 * height)))
        pygame.draw.rect(display, constants.BG_COLOR, (left + 5, top + 0.5 * width + 0.12 * height, width - 10, 3))
        top = top + 0.5 * width + 0.12 * height
        for action in self.actions:
            if action.condition_descr != "":
                to_render = action.condition_descr + ": " + action.description
            else:
                to_render = action.description
            text_render = font.render(to_render, True, constants.BG_COLOR)
            display.blit(text_render, (left + 50, top + 15))
            pygame.draw.rect(display, constants.BG_COLOR, (left + 25, top + 0.07 * height, width - 50, 3))
            top += 0.07 * height
        pygame.draw.rect(display, constants.BG_COLOR, (left + 5, top, width - 10, 3))

        if self.flavor_text != None:
            flavor = self.flavor_text.split('\n')
            top = rect[1] + constants.CARD_DISPLAY_Y_MARGIN + height * 0.9
            for text in flavor:
                text_render = font.render(text, True, constants.BG_COLOR)
                display.blit(text_render, (left + 15, top))
                top += height * 0.03

        return display
