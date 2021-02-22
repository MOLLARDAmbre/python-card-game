import pygame
import sys
from pygame.locals import *
from game import Game
from logger import Logger
from events import EventHandler, Event

def quit():
    log = Logger.get_instance()
    pygame.quit()
    log.log_info("Pygame quit")
    sys.exit(0)

def main():
    # TODO : design cards
    pygame.init()
    clock = pygame.time.Clock()
    FPS = 60
    game = Game()
    log = Logger.get_instance()
    event_handler = EventHandler.get_instance()
    event_handler.add_event_listener(Event.GAME_OVER, quit)
    log.log_info("Game initialisation complete")
    while True:  # Game loop
        game.update()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    event_handler.use_event(Event.MOVE_LEFT)
                if event.key == pygame.K_RIGHT:
                    event_handler.use_event(Event.MOVE_RIGHT)
                if event.key == pygame.K_DOWN:
                    event_handler.use_event(Event.MOVE_DOWN)
                if event.key == pygame.K_UP:
                    event_handler.use_event(Event.MOVE_UP)
                if event.key == pygame.K_RETURN:
                    event_handler.use_event(Event.VALID)
                if event.key == pygame.K_a:
                    event_handler.use_event(Event.TEST)

        clock.tick(FPS)


if __name__ == "__main__":
    main()
