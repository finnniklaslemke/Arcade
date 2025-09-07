import pygame
import sys
import random

import config
import screens

PLAYER_SPEED = 10
PLAYER_WIDTH = 10
PLAYER_HEIGHT = 100


class Player:
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos
        self.speed = PLAYER_SPEED
        self.dir = 0  # -1 up, 1 down, 0 still
        self.wins = 0

    def reset(self, x, y):
        self.pos.update(x, y)
        self.dir = 0


class Ball:
    def __init__(self):
        self.pos = pygame.Vector2(config.WIDTH / 2, config.HEIGHT / 2)
        self.radius = 10
        self.base_speed = 600
        # Start velocity: horizontal direction random left or right, vertical random small angle
        hor_dir = random.choice([-1, 1])
        vert_dir = random.uniform(-0.5, 0.5)
        self.vel = pygame.Vector2(hor_dir, vert_dir).normalize() * self.base_speed

    def update(self, dt):
        self.pos += self.vel * dt
        # Walls top and bottom
        if self.pos.y - self.radius <= 0:
            self.pos.y = self.radius
            self.vel.y *= -1
        elif self.pos.y + self.radius >= config.HEIGHT:
            self.pos.y = config.HEIGHT - self.radius
            self.vel.y *= -1
        # Left/right goal
        if self.pos.x - self.radius <= 0:
            self.on_goal('right')
        elif self.pos.x + self.radius >= config.WIDTH:
            self.on_goal('left')

    def on_goal(self, side):
        if side == 'right':
            self.opponent.wins += 1
        else:
            self.scorer.wins += 1
        self.pos = pygame.Vector2(config.WIDTH / 2, config.HEIGHT / 2)
        self.base_speed = 600
        # random angle in opponents direction
        hor_dir = -1 if side == 'right' else 1
        vert_dir = random.uniform(-0.5, 0.5)
        self.vel = pygame.Vector2(hor_dir, vert_dir).normalize() * self.base_speed
        self.game_state.game_over = True

    def draw(self, screen):
        pygame.draw.circle(screen, config.WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)


class GameState:
    def __init__(self):
        self.start_ticks = pygame.time.get_ticks()
        self.countdown_time = 3.0
        self.game_over = False
        self.show_settings = False
        self.paused = False
        self.show_quit_confirmation = False
        self.game_started = False
        self.go_to_menu = False


def handle_events(
        game_state,
        quit_screen,
        settings_screen,
        pause_screen,
        start_screen,
        game_over_screen,
        go_to_menu_screen
):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and (event.mod & pygame.KMOD_META):
                pygame.quit()
                sys.exit()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state.show_quit_confirmation:
            quit_screen.handle(game_state, event)
            return

        if game_state.go_to_menu:
            go_to_menu_screen.handle(game_state, event)
            return

        if game_state.show_settings:
            settings_screen.handle(game_state, event)
            return

        if game_state.game_over:
            game_over_screen.handle(game_state, event)
            return

        # Start screen handling
        if not game_state.game_started:
            start_screen.handle(game_state, event)
            return

        if not game_state.paused:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if game_state.countdown_time <= 0:
                    game_state.paused = True

            return

        if game_state.paused:
            pause_screen.handle(game_state, event)
            return

    return


def restart_game(player1, player2, game_state):
    player1.reset(20, config.HEIGHT // 2 - PLAYER_HEIGHT // 2)
    player2.reset(config.WIDTH - 20 - PLAYER_WIDTH, config.HEIGHT // 2 - PLAYER_HEIGHT // 2)
    game_state.game_over = False
    game_state.countdown_time = 3.0
    game_state.start_ticks = pygame.time.get_ticks()


def update_game(player1, player2, game_state, dt, ball):
    if not game_state.game_started:
        return
    if game_state.paused or game_state.game_over:
        return

    keys = pygame.key.get_pressed()

    if game_state.countdown_time > 0:
        game_state.countdown_time -= dt
        if game_state.countdown_time < 0:
            game_state.countdown_time = 0
        return

    if game_state.game_over:
        restart_game(player1, player2, game_state)

    # Paddle 1 movement (W/S)
    if keys[pygame.K_w]:
        player1.dir = -1
    elif keys[pygame.K_s]:
        player1.dir = 1
    else:
        player1.dir = 0

    # Paddle 2 movement (UP/DOWN)
    if keys[pygame.K_UP]:
        player2.dir = -1
    elif keys[pygame.K_DOWN]:
        player2.dir = 1
    else:
        player2.dir = 0

    # Update paddle positions
    player1.pos.y += player1.dir * player1.speed
    player2.pos.y += player2.dir * player2.speed

    # Clamp paddles inside screen
    player1.pos.y = max(0, min(config.HEIGHT - PLAYER_HEIGHT, player1.pos.y))
    player2.pos.y = max(0, min(config.HEIGHT - PLAYER_HEIGHT, player2.pos.y))

    # Update ball
    ball.update(dt)

    # Check ball collision with paddles
    paddle1_rect = pygame.Rect(player1.pos.x, player1.pos.y, PLAYER_WIDTH, PLAYER_HEIGHT)
    paddle2_rect = pygame.Rect(player2.pos.x, player2.pos.y, PLAYER_WIDTH, PLAYER_HEIGHT)

    ball_rect = pygame.Rect(ball.pos.x - ball.radius, ball.pos.y - ball.radius, ball.radius * 2, ball.radius * 2)

    SPEED_INCREMENT = 30

    if ball_rect.colliderect(paddle1_rect):
        # Reflect ball horizontally, add some vertical velocity based on hit position
        ball.pos.x = paddle1_rect.right + ball.radius
        ball.vel.x *= -1
        offset = (ball.pos.y - paddle1_rect.centery) / (PLAYER_HEIGHT / 2)
        ball.vel.y = offset * ball.base_speed * 0.75
        ball.base_speed += SPEED_INCREMENT
        ball.vel = ball.vel.normalize() * ball.base_speed

    elif ball_rect.colliderect(paddle2_rect):
        ball.pos.x = paddle2_rect.left - ball.radius
        ball.vel.x *= -1
        offset = (ball.pos.y - paddle2_rect.centery) / (PLAYER_HEIGHT / 2)
        ball.vel.y = offset * ball.base_speed * 0.75
        ball.base_speed += SPEED_INCREMENT
        ball.vel = ball.vel.normalize() * ball.base_speed


def draw_game(
        screen,
        player1,
        player2,
        game_state,
        pause_screen,
        start_screen,
        settings_screen,
        quit_screen,
        game_over_screen,
        go_to_menu_screen,
        ball
):
    screen.fill(config.BLACK)

    draw_score(screen, player1, player2)
    draw_players(screen, player1, player2)
    pygame.draw.rect(screen, config.WHITE, config.get_border(), width=config.border_width)
    pygame.draw.rect(screen, config.get_rect_below_border_color(), config.get_rect_below_border())

    ball.draw(screen)

    if game_state.game_started:
        # countdown
        if game_state.countdown_time > 0:
            countdown_font = pygame.font.SysFont(None, 150)
            countdown_text = countdown_font.render(str(int(game_state.countdown_time) + 1), True, config.WHITE)
            countdown_rect = countdown_text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 4))
            screen.blit(countdown_text, countdown_rect)

    if game_state.go_to_menu:
        go_to_menu_screen.draw_screen(config.screen)
    elif game_state.show_settings:
        settings_screen.draw_screen(config.screen)
    elif game_state.show_quit_confirmation:
        quit_screen.draw_screen(config.screen)
    elif not game_state.game_started:
        start_screen.draw_screen(config.screen)

    # Buttons only if quit confirmation is not shown
    if not game_state.show_quit_confirmation and not game_state.go_to_menu:
        if game_state.game_started:
            if game_state.show_settings:
                settings_screen.draw_screen(config.screen)

            elif game_state.paused:
                pause_screen.draw_screen(config.screen)

            elif game_state.game_over:
                game_over_screen.draw_screen(config.screen)


def draw_players(screen, player1, player2):
    # draw paddles
    pygame.draw.rect(screen, player1.color, (int(player1.pos.x), int(player1.pos.y), PLAYER_WIDTH, PLAYER_HEIGHT))
    pygame.draw.rect(screen, player2.color, (int(player2.pos.x), int(player2.pos.y), PLAYER_WIDTH, PLAYER_HEIGHT))


def draw_score(screen, player1, player2):
    text = config.fonts['score'].render(str(player1.wins), True, config.WHITE)
    rect = text.get_rect(center=(config.WIDTH // 4, 50))
    screen.blit(text, rect)

    text = config.fonts['score'].render(str(player2.wins), True, config.WHITE)
    rect = text.get_rect(center=((config.WIDTH // 4) * 3, 50))
    screen.blit(text, rect)


def main():

    pygame.init()

    pygame.display.set_caption("Pong")
    config.WIDTH, config.HEIGHT = config.screen.get_size()

    quit_screen = screens.QuitScreen()
    settings_screen = screens.SettingsScreen()
    pause_screen = screens.PauseScreen()
    start_screen = screens.StartScreen()
    game_over_screen = screens.GameOverScreen(lambda: restart_game(player1, player2, game_state))
    go_to_menu_screen = screens.GoToMenuScreen()

    player1 = Player(config.PURPLE, pygame.Vector2(20, config.HEIGHT // 2 - PLAYER_HEIGHT // 2))
    player2 = Player(config.LIGHT_BLUE, pygame.Vector2(config.WIDTH - 20 - PLAYER_WIDTH, config.HEIGHT // 2 - PLAYER_HEIGHT // 2))

    game_state = GameState()

    ball = Ball()
    ball.scorer = player1
    ball.opponent = player2
    ball.game_state = game_state

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000

        handle_events(game_state, quit_screen, settings_screen, pause_screen, start_screen, game_over_screen, go_to_menu_screen)

        if game_state.paused or not game_state.game_started or game_state.game_over:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

        update_game(player1, player2, game_state, dt, ball)

        player1.color = config.PURPLE
        player2.color = config.LIGHT_BLUE

        draw_game(
            config.screen,
            player1,
            player2,
            game_state,
            pause_screen,
            start_screen,
            settings_screen,
            quit_screen,
            game_over_screen,
            go_to_menu_screen,
            ball
        )

        pygame.display.flip()


if __name__ == "__main__":
    main()