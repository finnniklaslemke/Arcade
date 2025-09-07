import pygame
import sys
import numpy as np

import config
import screens

ROWS, COLS = 6, 7
SQUARE_SIZE = 100
RADIUS = SQUARE_SIZE // 2 - 5


class Player:
    def __init__(self, player_id, color, left_key, right_key, drop_key):
        self.id = player_id
        self.color = color
        self.left_key = left_key
        self.right_key = right_key
        self.drop_key = drop_key
        self.score = 0
        self.current_col = 3
        self.is_turn = False

    def move_left(self):
        self.current_col = max(0, self.current_col - 1)

    def move_right(self):
        self.current_col = min(COLS - 1, self.current_col + 1)

    def increment_score(self):
        self.score += 1

class GameState:
    def __init__(self):
        self.board = create_board()
        self.players = [
            Player(1, config.PURPLE, pygame.K_a, pygame.K_d, pygame.K_s),
            Player(2, config.LIGHT_BLUE, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN)
        ]
        self.game_over = False
        self.winner_found = False
        self.show_settings = False
        self.paused = False
        self.show_quit_confirmation = False
        self.game_started = False
        self.go_to_menu = False
        self.choose_starting_player = True
        self.choose_game = False
        self.dropping = False
        self.drop_col = None
        self.drop_row = None
        self.drop_y = None

def check_winner(game_state):
    rows = len(game_state.board)
    cols = len(game_state.board[0])
    winner = 0

    for r in range(rows):
        for c in range(cols):
            player = game_state.board[r][c]
            if player == 0:
                continue
            # Horizontal
            if c <= cols - 4 and all(game_state.board[r][c+i] == player for i in range(4)):
                winner = player
            # Vertikal
            elif r <= rows - 4 and all(game_state.board[r+i][c] == player for i in range(4)):
                winner = player
            # Diagonal ↘
            elif r <= rows - 4 and c <= cols - 4 and all(game_state.board[r+i][c+i] == player for i in range(4)):
                winner = player
            # Diagonal ↗
            elif r >= 3 and c <= cols - 4 and all(game_state.board[r-i][c+i] == player for i in range(4)):
                winner = player
            if winner in (1, 2):
                game_state.players[int(winner)-1].increment_score()
                game_state.winner_found = True
                return

def get_winning_positions(board):
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            player = board[r][c]
            if player == 0:
                continue
            # Horizontal
            if c <= cols - 4 and all(board[r][c+i] == player for i in range(4)):
                return [(r, c+i) for i in range(4)]
            # Vertikal
            if r <= rows - 4 and all(board[r+i][c] == player for i in range(4)):
                return [(r+i, c) for i in range(4)]
            # Diagonal ↘
            if r <= rows - 4 and c <= cols - 4 and all(board[r+i][c+i] == player for i in range(4)):
                return [(r+i, c+i) for i in range(4)]
            # Diagonal ↗
            if r >= 3 and c <= cols - 4 and all(board[r-i][c+i] == player for i in range(4)):
                return [(r-i, c+i) for i in range(4)]
    return []

def piece_color(piece):
    return config.PURPLE if piece == 1 else config.LIGHT_BLUE

def handle_events(
        game_state,
        quit_screen,
        settings_screen,
        pause_screen,
        start_screen,
        game_over_screen,
        go_to_menu_screen,
        choose_starting_player_screen,
):
    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_q and (event.mod & pygame.KMOD_META)) or event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state.winner_found and not game_state.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and game_state.restart_button_rect and game_state.restart_button_rect.collidepoint(event.pos):
                restart_game(game_state)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state.game_over = True
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    restart_game(game_state)
            return

        for cond, scr in [
            (game_state.show_settings, settings_screen),
            (game_state.show_quit_confirmation, quit_screen),
            (game_state.go_to_menu, go_to_menu_screen),
            (game_state.choose_starting_player, choose_starting_player_screen),
            (game_state.game_over, game_over_screen)
        ]:
            if cond:
                scr.handle(game_state, event)
                return

        # Only handle pause and movement/drop controls if not paused and not game over
        if not game_state.paused and not game_state.game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state.paused = True
                return
            current_player = next(p for p in game_state.players if p.is_turn)
            if not game_state.dropping:
                if event.key == current_player.left_key:
                    current_player.move_left()
                elif event.key == current_player.right_key:
                    current_player.move_right()
                elif event.key == current_player.drop_key and is_valid_location(game_state.board, current_player.current_col):
                    row = get_next_open_row(game_state.board, current_player.current_col)
                    game_state.dropping = True
                    game_state.drop_col = current_player.current_col
                    game_state.drop_row = row
                    game_state.drop_y = (config.HEIGHT - (ROWS + 1) * SQUARE_SIZE)//2 + SQUARE_SIZE//2
            return
        if game_state.paused:
            pause_screen.handle(game_state, event)
            return

def create_board():
    return np.zeros((ROWS, COLS), int)

def is_valid_location(board, col):
    return board[0][col] == 0

def get_next_open_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            return r

def draw_board(board, offset_x, offset_y):
    winning_positions = get_winning_positions(board)
    for c in range(COLS):
        for r in range(ROWS):
            color = {1: config.PURPLE, 2: config.LIGHT_BLUE}.get(board[r][c], config.BLACK)
            x = offset_x + c * SQUARE_SIZE + SQUARE_SIZE // 2
            y = offset_y + r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(config.screen, config.WHITE, (x, y), RADIUS + 3)
            pygame.draw.circle(config.screen, color, (x, y), RADIUS)
    if winning_positions:
        start_r, start_c = winning_positions[0]
        end_r, end_c = winning_positions[-1]
        pygame.draw.line(
            config.screen,
            config.WHITE,
            (offset_x + start_c * SQUARE_SIZE + SQUARE_SIZE // 2,
             offset_y + start_r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE // 2),
            (offset_x + end_c * SQUARE_SIZE + SQUARE_SIZE // 2,
             offset_y + end_r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE // 2),
            8
        )

# Draw the active piece at the top
def draw_active_piece(piece, col, offset_x, offset_y):
    color = piece_color(piece)
    pygame.draw.circle(
        config.screen,
        color,
        (
            offset_x + col * SQUARE_SIZE + SQUARE_SIZE // 2,
            offset_y + SQUARE_SIZE // 2
        ),
        RADIUS
    )

def restart_game(game_state):
    game_state.choose_starting_player = True
    game_state.game_started = False
    game_state.game_over = False
    game_state.winner_found = False
    game_state.board = create_board()

def draw_game(
        screen,
        game_state,
        pause_screen,
        start_screen,
        settings_screen,
        quit_screen,
        game_over_screen,
        go_to_menu_screen,
        choose_starting_player_screen,
):
    screen.fill(config.BLACK)
    offset_x = (config.WIDTH - COLS * SQUARE_SIZE) // 2
    offset_y = (config.HEIGHT - (ROWS + 1) * SQUARE_SIZE) // 2

    if not game_state.game_over and not game_state.winner_found:
        check_winner(game_state)

    pygame.draw.rect(screen, config.WHITE, config.get_border(), width=config.border_width)
    pygame.draw.rect(screen, config.get_rect_below_border_color(), config.get_rect_below_border())
    draw_score(screen, game_state.players[0].score, game_state.players[1].score)

    # Draw active piece at top if not dropping
    if not game_state.dropping and not game_state.winner_found:
        current_player = next(p for p in game_state.players if p.is_turn)
        draw_active_piece(current_player.id, current_player.current_col, offset_x, offset_y)

    draw_board(game_state.board, offset_x, offset_y)
    # Draw the two white rectangles (board borders) after the board
    pygame.draw.rect(screen, config.WHITE, pygame.Rect(offset_x - 25, offset_y + SQUARE_SIZE, SQUARE_SIZE * COLS + 50, SQUARE_SIZE * ROWS), width=3)
    pygame.draw.rect(screen, config.WHITE, pygame.Rect(offset_x - 50, offset_y + SQUARE_SIZE * (ROWS + 1), SQUARE_SIZE * COLS + 100, 50), width=3)
    # Draw falling piece if dropping, after board and borders
    if game_state.dropping:
        col = game_state.drop_col
        drop_y = game_state.drop_y
        current_player = next(p for p in game_state.players if p.is_turn)
        piece = current_player.id
        color = piece_color(piece)
        if col is not None and drop_y is not None:
            pygame.draw.circle(
                config.screen,
                color,
                (
                    offset_x + col * SQUARE_SIZE + SQUARE_SIZE // 2,
                    int(drop_y)
                ),
                RADIUS
            )

    # Centralized overlays/screens
    for cond, scr in [
        (game_state.go_to_menu, go_to_menu_screen),
        (game_state.show_settings, settings_screen),
        (game_state.show_quit_confirmation, quit_screen),
        (game_state.choose_starting_player, choose_starting_player_screen),
        (game_state.paused, pause_screen),
        (game_state.game_over, game_over_screen)
    ]:
        if cond:
            screen.fill(config.BLACK)
            scr.draw_screen(config.screen)
            return
    # Draw restart button if winner found (above the board)
    if game_state.winner_found:
        restart_rect = pygame.Rect(0, 0, *config.buttons['standard_size'])
        restart_rect.center = (config.WIDTH // 2, config.HEIGHT // 5)
        game_state.restart_button_rect = restart_rect
        text = config.fonts['selected_button'].render('Restart', True, config.WHITE)
        screen.blit(text, text.get_rect(center=restart_rect.center))

def draw_score(screen, player1_wins, player2_wins):
    for i, score in enumerate([player1_wins, player2_wins]):
        text = config.fonts['score'].render(str(score), True, config.WHITE)
        rect = text.get_rect(center=(config.WIDTH//4*(1+2*i), 50))
        screen.blit(text, rect)


def main():
    pygame.init()

    pygame.display.set_caption("Connect 4")

    game_state = GameState()

    quit_screen = screens.QuitScreen()
    settings_screen = screens.SettingsScreen()
    pause_screen = screens.PauseScreen()
    start_screen = screens.StartScreen()
    game_over_screen = screens.GameOverScreen(lambda: restart_game(game_state))
    go_to_menu_screen = screens.GoToMenuScreen()
    choose_starting_player_screen = screens.ChooseStartingPlayerScreen()

    drop_speed = 18  # pixels per frame for falling piece

    offset_y = (config.HEIGHT - (ROWS + 1) * SQUARE_SIZE) // 2
    while True:
        # Animate drop if in progress
        if game_state.dropping:
            col, row, dy = game_state.drop_col, game_state.drop_row, game_state.drop_y
            if col is not None and row is not None and dy is not None:
                target_y = offset_y + (row+1)*SQUARE_SIZE + SQUARE_SIZE//2
                game_state.drop_y = min(dy + drop_speed, target_y)
                if game_state.drop_y == target_y:
                    cp = next(p for p in game_state.players if p.is_turn)
                    game_state.board[row][col] = cp.id
                    [setattr(p, 'is_turn', not p.is_turn) for p in game_state.players]
                    game_state.dropping = False
                    game_state.drop_col = game_state.drop_row = game_state.drop_y = None
                    cp.current_col = 3

        if not game_state.choose_starting_player:
            draw_game(
                config.screen,
                game_state,
                pause_screen,
                start_screen,
                settings_screen,
                quit_screen,
                game_over_screen,
                go_to_menu_screen,
                choose_starting_player_screen,
            )
        else:
            config.screen.fill(config.BLACK)
            if game_state.show_settings:
                settings_screen.draw_screen(config.screen)
            elif game_state.go_to_menu:
                go_to_menu_screen.draw_screen(config.screen)
            elif game_state.show_quit_confirmation:
                quit_screen.draw_screen(config.screen)
            else:
                choose_starting_player_screen.draw_screen(config.screen)

        handle_events(
            game_state,
            quit_screen,
            settings_screen,
            pause_screen,
            start_screen,
            game_over_screen,
            go_to_menu_screen,
            choose_starting_player_screen,
        )

        if game_state.paused or not game_state.game_started or game_state.game_over or game_state.winner_found:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

        pygame.display.update()


if __name__ == "__main__":
    main()