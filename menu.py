import pygame
import sys

import config
from minigames import trails as trail_game
from minigames import connectFour as connectFour
from minigames import pong as pong
from minigames import trailPong as trailPong
import screens


class MenuState:
    def __init__(self):
        self.show_choose_game = False
        self.show_settings = False
        self.show_quit_confirmation = False

def handle_events(menu_state, menu_screen, settings_screen, choose_game_screen, quit_screen):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and (event.mod & pygame.KMOD_META):
                pygame.quit()
                sys.exit()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if menu_state.show_quit_confirmation:
            quit_screen.handle(menu_state, event)
        elif menu_state.show_choose_game:
            choose_game_screen.handle(menu_state, event)
        elif menu_state.show_settings:
            settings_screen.handle(menu_state, event)
        else:
            menu_screen.handle(menu_state, event)


def main():

    pygame.init()
    config.fonts['standard_button'] = pygame.font.SysFont(None, 50)
    config.fonts['selected_button'] = pygame.font.SysFont(None, 65)
    config.fonts['score'] = pygame.font.SysFont(None, 40)

    config.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Arcade")
    config.WIDTH, config.HEIGHT = pygame.display.get_surface().get_size()

    menu_screen = screens.MenuScreen()
    settings_screen = screens.SettingsScreen()
    choose_game_screen = screens.ChooseGameScreen(lambda: trail_game.main(), lambda: connectFour.main(), lambda: pong.main(), lambda: trailPong.main())
    quit_screen = screens.QuitScreen()

    menu_state = MenuState()

    while True:

        handle_events(menu_state, menu_screen, settings_screen, choose_game_screen, quit_screen)
        pygame.mouse.set_visible(True)

        if menu_state.show_quit_confirmation:
            config.screen.fill(config.BLACK)
            quit_screen.draw_screen(config.screen)
        elif menu_state.show_choose_game:
            choose_game_screen.draw_screen(config.screen)
        elif menu_state.show_settings:
            config.screen.fill(config.BLACK)
            settings_screen.draw_screen(config.screen)
        else:
            menu_screen.draw_screen(config.screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()