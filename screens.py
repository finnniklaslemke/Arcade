import pygame
import sys

import config
import menu

class ScreenBase:
    def __init__(self, button_names):
        self.buttons_name = button_names
        self.selected = button_names[0]
        self.cur_key = 0
        w, h = pygame.display.get_surface().get_size()
        self.buttons = {}
        for i, name in enumerate(button_names):
            rect = pygame.Rect(0, 0, *config.buttons['standard_size'])
            rect.center = (
                w // 2,
                h // 2 - (len(button_names) * config.buttons['height']) // 2
                + config.buttons['height'] // 2 + i * config.buttons['height']
            )
            self.buttons[name] = rect

    def scroll(self, event):
        if event.key == pygame.K_DOWN:
            self.cur_key = (self.cur_key + 1) % len(self.buttons_name)
        elif event.key == pygame.K_UP:
            self.cur_key = (self.cur_key - 1) % len(self.buttons_name)
        self.selected = self.buttons_name[self.cur_key]

    def handle(self, state, event):
        # Hover-Highlight
        if event.type == pygame.MOUSEMOTION:
            for name in self.buttons_name:
                if self.buttons[name].collidepoint(event.pos):
                    if self.selected != name:
                        self.selected = name
                        self.cur_key = self.buttons_name.index(name)
                    break

        # Click-Handling
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name in self.buttons_name:
                if self.buttons[name].collidepoint(event.pos):
                    idx = self.buttons_name.index(name)
                    if self.selected == name:
                        self.handle_selection(self.selected, state, mouse=True)
                    else:
                        self.selected = name
                        self.cur_key = idx
                    return
        # Keyboard navigation and selection
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.scroll(event)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.handle_selection(self.selected, state, mouse=False)

    def handle_selection(self, selection, state, mouse=False):
        # To be implemented by subclasses
        pass

    def draw_buttons(self, screen, label_overrides=None):
        label_overrides = label_overrides or {}
        for name in self.buttons_name:
            rect = self.buttons[name]
            selected = (name == self.selected)
            if selected:
                text_color = config.WHITE
                font = config.fonts['selected_button']
                if self.selected == 'player 1 starts':
                    text_color = config.PURPLE
                elif self.selected == 'player 2 starts':
                    text_color = config.LIGHT_BLUE
            else:
                text_color = config.LIGHT_GREY
                font = config.fonts['standard_button']

            label = label_overrides.get(name, name)
            text_surf = font.render(label.title(), True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

            pygame.draw.rect(screen, config.WHITE, config.get_border(), width=config.border_width)
            pygame.draw.rect(screen, config.get_rect_below_border_color(), config.get_rect_below_border())

class ChooseStartingPlayerScreen(ScreenBase):
    def __init__(self):
        super().__init__(['player 1 starts', 'player 2 starts', 'settings', 'menu', 'quit'])

    def handle_selection(self, selection, game_state, mouse=False):
        match selection:
            case 'player 1 starts':
                game_state.players[0].is_turn = True
                game_state.players[1].is_turn = False
                game_state.choose_starting_player = False
                game_state.game_started = True
            case 'player 2 starts':
                game_state.players[0].is_turn = False
                game_state.players[1].is_turn = True
                game_state.choose_starting_player = False
                game_state.game_started = True
            case 'settings':
                game_state.show_settings = True
            case 'menu':
                game_state.go_to_menu = True
            case 'quit':
                game_state.show_quit_confirmation = True
        return


    def draw_screen(self, screen):
        self.draw_buttons(screen)



class MenuScreen(ScreenBase):
    def __init__(self):
        super().__init__(['choose game', 'settings', 'quit'])

    def handle_selection(self, selection, menu_state, mouse=False):
        match selection:
            case 'choose game':
                menu_state.show_choose_game = True
            case 'settings':
                menu_state.show_settings = True
            case 'quit':
                menu_state.show_quit_confirmation = True

    def draw_screen(self, screen):
        screen.fill(config.BLACK)
        self.draw_buttons(screen)


class GoToMenuScreen(ScreenBase):
    def __init__(self):
        super().__init__(['menu', 'back'])

    def handle_selection(self, selection, game_state, mouse=False):
        match selection:
            case 'menu':
                menu.main()
            case 'back':
                game_state.go_to_menu = False
        # Reset to default if closed
        if not game_state.go_to_menu:
            self.cur_key = 0
            self.selected = 'menu'

    def draw_screen(self, screen):
        self.draw_buttons(screen)

class ChooseGameScreen(ScreenBase):
    def __init__(self, start_trails_game_callback, start_connect_four_callback, start_pong_callback, start_trail_pong_callback):
        self.start_trails_game_callback = start_trails_game_callback
        self.start_connect_four_callback = start_connect_four_callback
        self.start_pong_callback = start_pong_callback
        self.start_trail_pong_callback = start_trail_pong_callback
        super().__init__(['trails', 'pong', 'trail pong', 'connect 4', 'back'])

    def handle_selection(self, selection, menu_state, mouse=False):
        match selection:
            case 'trails':
                self.start_trails_game_callback()
            case 'pong':
                self.start_pong_callback()
            case 'trail pong':
                self.start_trail_pong_callback()
            case 'connect 4':
                self.start_connect_four_callback()
            case 'back':
                menu_state.show_choose_game = False
        if not menu_state.show_choose_game:
            self.cur_key = 0
            self.selected = 'trails'

    def draw_screen(self, screen):
        screen.fill(config.BLACK)
        self.draw_buttons(screen)


class QuitScreen(ScreenBase):
    def __init__(self):
        super().__init__(['exit', 'back'])

    def handle_selection(self, selection, game_state, mouse=False):
        match selection:
            case 'exit':
                pygame.quit()
                sys.exit()
            case 'back':
                game_state.show_quit_confirmation = False
        if not game_state.show_quit_confirmation:
            self.cur_key = 0
            self.selected = 'exit'

    def draw_screen(self, screen):
        self.draw_buttons(screen)


class SettingsScreen(ScreenBase):
    def __init__(self):
        super().__init__(['color_mode', 'back'])

    def get_color_button_name(self):
        return 'darkmode' if not config.darkmode else 'whitemode'

    def switch_color_mode(self):
        x = config.WHITE
        config.WHITE = config.BLACK
        config.BLACK = x

        x = config.LIGHT_BLUE
        config.LIGHT_BLUE = config.BLUE
        config.BLUE = x

        x = config.PURPLE
        config.PURPLE = config.RED
        config.RED = x

        config.darkmode = not config.darkmode

    def handle_selection(self, selection, game_state, mouse=False):
        match selection:
            case 'color_mode':
                self.switch_color_mode()
            case 'back':
                game_state.show_settings = False
        if not game_state.show_settings:
            self.cur_key = 0
            self.selected = 'color_mode'

    def draw_screen(self, screen):
        labels = {'color_mode': self.get_color_button_name()}
        self.draw_buttons(screen, label_overrides=labels)


class PauseScreen(ScreenBase):
    def __init__(self):
        super().__init__(['resume', 'settings', 'menu', 'quit'])

    def handle_selection(self, selection, game_state, mouse=False):
        match selection:
            case 'resume':
                game_state.paused = False
                game_state.countdown_time = 3.0
                game_state.start_ticks = pygame.time.get_ticks()
            case 'settings':
                game_state.show_settings = True
            case 'menu':
                game_state.go_to_menu = True
            case 'quit':
                game_state.show_quit_confirmation = True
        if game_state.show_settings or game_state.show_quit_confirmation or game_state.go_to_menu or not game_state.paused:
            self.cur_key = 0
            self.selected = 'resume'

    def draw_screen(self, screen):
        self.draw_buttons(screen)


class StartScreen(ScreenBase):
    def __init__(self):
        super().__init__(['start', 'settings', 'menu', 'quit'])

    def handle_selection(self, selection, game_state, mouse=False):
        match selection:
            case 'start':
                game_state.game_started = True
                game_state.countdown_time = 3.0
                game_state.start_ticks = pygame.time.get_ticks()
            case 'settings':
                game_state.show_settings = True
            case 'menu':
                game_state.go_to_menu = True
            case 'quit':
                game_state.show_quit_confirmation = True
        if game_state.show_settings or game_state.show_quit_confirmation or game_state.go_to_menu or game_state.game_started:
            self.cur_key = 0
            self.selected = 'start'

    def draw_screen(self, screen):
        self.draw_buttons(screen)


class GameOverScreen(ScreenBase):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        super().__init__(['restart', 'settings', 'menu', 'quit'])

    def handle_selection(self, selection, game_state, mouse=False):
        match selection:
            case 'restart':
                self.restart_callback()
            case 'settings':
                game_state.show_settings = True
            case 'menu':
                game_state.go_to_menu = True
            case 'quit':
                game_state.show_quit_confirmation = True
        if game_state.show_settings or game_state.show_quit_confirmation or game_state.go_to_menu:
            self.cur_key = 0
            self.selected = 'restart'

    def draw_screen(self, screen):
        self.draw_buttons(screen)