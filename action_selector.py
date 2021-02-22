import pygame
import constants
from events import *

class ActionSelector():
    """
    Piece of ui designed to select the action to use on a card
    """
    def __init__(self, parent, actions, rect):
        self.parent = parent  # Original ui to go back to
        self.actions = actions  # Action list to display
        self.draw_space = rect
        self.actions_enabled = False
        self.handler_valid = lambda : self.handle_valid()
        self.handler_up = lambda : self.handle_up()
        self.handler_down = lambda : self.handle_down()
        self.cursor_pos = 0
        EventHandler.get_instance().add_event_listener(Event.VALID, self.handler_valid)
        EventHandler.get_instance().add_event_listener(Event.MOVE_UP, self.handler_up)
        EventHandler.get_instance().add_event_listener(Event.MOVE_DOWN, self.handler_down)

    def draw(self, display):
        font = pygame.font.SysFont(None, 24)
        left, top, width, height = self.draw_space
        pygame.draw.rect(display, constants.BLACK, self.draw_space)
        for i in range(len(self.actions) - 1):
            pygame.draw.rect(display, constants.BG_COLOR, (left, top + int((i+1) * height / len(self.actions)), width, 1))
        for action_nb in range(len(self.actions)):
            action = self.actions[action_nb]
            if action_nb == self.cursor_pos:
                col = constants.CURSOR_COLOR
            else:
                col = constants.BG_COLOR
            text_render = font.render(action.description, True, col)
            text_render = pygame.transform.scale(text_render, (min(constants.ACTION_SELECTOR_WIDTH - 15, 20*len(action.description)), min(constants.ACTION_SELECTOR_HEIGHT - 5, 100)))  # Ensure the text fits the box (while still looking decent with the mins)
            display.blit(text_render, (left + 5, top + action_nb * constants.ACTION_SELECTOR_HEIGHT + 5))

    def close(self, choosen_action):
        self.parent.close_selector(choosen_action)

    def handle_valid(self):
        if not self.actions_enabled:
            return
        EventHandler.get_instance().remove_event_listener(Event.VALID, self.handler_valid)
        EventHandler.get_instance().remove_event_listener(Event.MOVE_UP, self.handler_up)
        EventHandler.get_instance().remove_event_listener(Event.MOVE_DOWN, self.handler_down)
        self.close(self.actions[self.cursor_pos])
        del self

    def handle_down(self):
        self.cursor_pos += 1
        if self.cursor_pos == len(self.actions):
            self.cursor_pos = 0

    def handle_up(self):
        self.cursor_pos -= 1
        if self.cursor_pos == -1:
            self.cursor_pos = len(self.actions) - 1
