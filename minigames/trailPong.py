import pygame
import sys
import random

import config
import screens
import math

PLAYER_SPEED = 7
PLAYER_SIZE = 30
TRAIL_LENGTH = 30
GROWTH_PER_SECOND = 10


class Player:
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos
        self.speed = PLAYER_SPEED
        self.trail = []
        self.dir = pygame.Vector2(0, -1)
        self.wins = 0
        self.trail_length = TRAIL_LENGTH

    def reset(self, x, y):
        self.pos.update(x, y)
        self.dir = pygame.Vector2(0, -1)
        self.trail.clear()

class Ball:
    def __init__(self):
        self.pos = pygame.Vector2(config.WIDTH/2, config.HEIGHT/2)
        self.radius = 10
        self.base_speed = 350
        angle = random.uniform(0, 2 * math.pi)
        self.vel = pygame.Vector2(1, 0).rotate_rad(angle).normalize() * self.base_speed
        self.last_collision_time = 0.0
        self.collision_cooldown = 0.06  # seconds; prevents rapid re-collisions on trails


    def update(self, dt):
        self.pos += self.vel * dt
        # walls top and bottom
        if self.pos.y - self.radius <= 0 or self.pos.y + self.radius >= config.HEIGHT:
            self.vel.y *= -1
            self.vel = self.vel.normalize() * self.base_speed
        # left / right goal
        if self.pos.x - self.radius <= 0:
            self.on_goal('right')
        elif self.pos.x + self.radius >= config.WIDTH:
            self.on_goal('left')

    def on_goal(self, side):
        if side == 'right':
            self.opponent.wins += 1
        else:
            self.scorer.wins += 1
        self.pos = pygame.Vector2(config.WIDTH/2, config.HEIGHT/2)
        vert_dir = random.uniform(-1, 1)
        if side == 'right':
            self.vel = pygame.Vector2(-1, vert_dir).normalize() * self.base_speed
        else:
            self.vel = pygame.Vector2(1, vert_dir).normalize() * self.base_speed
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
    player1.reset(config.WIDTH // 4, config.HEIGHT // 2)
    player2.reset(3 * config.WIDTH // 4, config.HEIGHT // 2)
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

    move_dir1 = pygame.Vector2(player1.dir)
    # edit y-component
    if keys[pygame.K_w]:
        move_dir1.y = -1
    elif keys[pygame.K_s]:
        move_dir1.y = 1
    else:
        move_dir1.y = 0
    # edit x-component
    if keys[pygame.K_a]:
        move_dir1.x = -1
    elif keys[pygame.K_d]:
        move_dir1.x = 1
    else:
        move_dir1.x = 0
    if move_dir1.length() > 0:
        move_dir1 = move_dir1.normalize()
        player1.dir = move_dir1

    move_dir2 = pygame.Vector2(player2.dir)
    # edit y-component
    if keys[pygame.K_UP]:
        move_dir2.y = -1
    elif keys[pygame.K_DOWN]:
        move_dir2.y = 1
    else:
        move_dir2.y = 0
    # edit x-component
    if keys[pygame.K_LEFT]:
        move_dir2.x = -1
    elif keys[pygame.K_RIGHT]:
        move_dir2.x = 1
    else:
        move_dir2.x = 0
    if move_dir2.length() > 0:
        move_dir2 = move_dir2.normalize()
        player2.dir = move_dir2

    player1.pos += player1.dir * player1.speed
    player2.pos += player2.dir * player2.speed

    # check screen borders
    player1.pos.x = max(0, min(config.WIDTH - PLAYER_SIZE, player1.pos.x))
    player1.pos.y = max(0, min(config.HEIGHT - PLAYER_SIZE, player1.pos.y))
    player2.pos.x = max(0, min(config.WIDTH - PLAYER_SIZE, player2.pos.x))
    player2.pos.y = max(0, min(config.HEIGHT - PLAYER_SIZE, player2.pos.y))

    # update trails
    player1.trail.append(player1.pos + pygame.Vector2(PLAYER_SIZE / 2, PLAYER_SIZE / 2))
    player2.trail.append(player2.pos + pygame.Vector2(PLAYER_SIZE / 2, PLAYER_SIZE / 2))

    if len(player1.trail) > player1.trail_length:
        player1.trail.pop(0)
    if len(player2.trail) > player2.trail_length:
        player2.trail.pop(0)

    # update ball
    ball.update(dt)

    # check ball collision with trails (Einfallswinkel = Ausfallswinkel)
    now = pygame.time.get_ticks() / 1000.0
    trail_r = PLAYER_SIZE // 10

    # Player 1 trail collision (with cooldown + depenetration)
    if now - ball.last_collision_time >= ball.collision_cooldown:
        seen = []
        for pos in player1.trail:
            if not any(pos == s for s in seen):
                seen.append(pos)
                to_center = ball.pos - pos
                dist = to_center.length()
                if dist < ball.radius + trail_r:
                    normal = to_center.normalize() if dist != 0 else pygame.Vector2(1, 0)
                    ball.vel = ball.vel.reflect(normal)
                    ball.vel = ball.vel.normalize() * ball.base_speed
                    # Push the ball out of the trail circle to avoid re-colliding next frame
                    overlap = (ball.radius + trail_r - dist) if dist != 0 else (ball.radius + trail_r)
                    ball.pos += normal * (overlap + 0.5)
                    ball.last_collision_time = now
                    break

    # Player 2 trail collision (with cooldown + depenetration)
    if now - ball.last_collision_time >= ball.collision_cooldown:
        seen = []
        for pos in player2.trail:
            if not any(pos == s for s in seen):
                seen.append(pos)
                to_center = ball.pos - pos
                dist = to_center.length()
                if dist < ball.radius + trail_r:
                    normal = to_center.normalize() if dist != 0 else pygame.Vector2(1, 0)
                    ball.vel = ball.vel.reflect(normal)
                    ball.vel = ball.vel.normalize() * ball.base_speed
                    overlap = (ball.radius + trail_r - dist) if dist != 0 else (ball.radius + trail_r)
                    ball.pos += normal * (overlap + 0.5)
                    ball.last_collision_time = now
                    break


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
            # pause screen
            elif game_state.paused:
                pause_screen.draw_screen(config.screen)

            elif game_state.game_over:
                game_over_screen.draw_screen(config.screen)


def draw_players(screen, player1, player2):
    # draw trails
    trail_length = len(player1.trail)
    for i, pos in enumerate(player1.trail):
        alpha = int(50 + 205 * (i / trail_length))
        color = (*player1.color[:3], alpha)
        trail_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(trail_surf, color, (PLAYER_SIZE // 2, PLAYER_SIZE // 2), PLAYER_SIZE // 10)
        screen.blit(trail_surf, (int(pos.x - PLAYER_SIZE // 2), int(pos.y - PLAYER_SIZE // 2)))

    trail_length = len(player2.trail)
    for i, pos in enumerate(player2.trail):
        alpha = int(50 + 205 * (i / trail_length))
        color = (*player2.color[:3], alpha)
        trail_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(trail_surf, color, (PLAYER_SIZE // 2, PLAYER_SIZE // 2), PLAYER_SIZE // 10)
        screen.blit(trail_surf, (int(pos.x - PLAYER_SIZE // 2), int(pos.y - PLAYER_SIZE // 2)))

    # draw player
    pygame.draw.circle(screen, player1.color, (int(player1.pos.x + PLAYER_SIZE / 2), int(player1.pos.y + PLAYER_SIZE / 2)), PLAYER_SIZE // 3)
    pygame.draw.circle(screen, player2.color, (int(player2.pos.x + PLAYER_SIZE / 2), int(player2.pos.y + PLAYER_SIZE / 2)), PLAYER_SIZE // 3)

def draw_score(screen, player1, player2):
    text = config.fonts['score'].render(str(player1.wins), True, config.WHITE)
    rect = text.get_rect(center=(config.WIDTH // 4, 50))
    screen.blit(text, rect)

    text = config.fonts['score'].render(str(player2.wins), True, config.WHITE)
    rect = text.get_rect(center=((config.WIDTH // 4) * 3, 50))
    screen.blit(text, rect)


def main():

    pygame.init()

    pygame.display.set_caption("Trail Pong")
    config.WIDTH, config.HEIGHT = config.screen.get_size()

    quit_screen = screens.QuitScreen()
    settings_screen = screens.SettingsScreen()
    pause_screen = screens.PauseScreen()
    start_screen = screens.StartScreen()
    game_over_screen = screens.GameOverScreen(lambda: restart_game(player1, player2, game_state))
    go_to_menu_screen = screens.GoToMenuScreen()

    player1 = Player(config.PURPLE, pygame.Vector2(config.WIDTH // 4 - 15, config.HEIGHT // 2 - 15))
    player2 = Player(config.LIGHT_BLUE, pygame.Vector2(3 * config.WIDTH // 4 - 15, config.HEIGHT // 2 - 15))

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