import pygame

WIDTH = 700
CARD_DISPLAY_WIDTH = 500
HEIGHT = 700
BG_COLOR = (255, 255, 255)
BLACK = (0, 0, 0)
CURSOR_COLOR = (0, 255, 150)
CARD_DISPLAY_X_MARGIN = int(WIDTH * 0.05)
CARD_DISPLAY_Y_MARGIN = int(HEIGHT * 0.05)
CARD_WIDTH = int(WIDTH * 0.13)
CARD_HEIGHT = int(HEIGHT * 0.13)
CARD_SPACING = int(WIDTH * 0.03)
CARD_X_MARGIN = int(WIDTH * 0.1)
ACTION_SELECTOR_WIDTH = int(WIDTH * 0.3)
ACTION_SELECTOR_HEIGHT = int(HEIGHT * 0.05)
POINTS_MARQUER_SIZE = int(WIDTH * 0.1)

MIDDLE_0_COLOR = (83, 255, 247)
MIDDLE_1_COLOR = (209, 215, 79)
MIDDLE_2_COLOR = (252, 165, 255)
MIDDLE_3_COLOR = (165, 173, 255)
MIDDLE_4_COLOR = (144, 255, 118)

def get_middle_color(i):
    if i == 0:
        return MIDDLE_0_COLOR
    if i == 1:
        return MIDDLE_1_COLOR
    if i == 2:
        return MIDDLE_2_COLOR
    if i == 3:
        return MIDDLE_3_COLOR
    return MIDDLE_4_COLOR
