"""
GameEngine: owns the puck, both paddles, and the computer AI, and runs
one frame's worth of game logic.

Starter version: the puck bounces around and paddles can hit it, but
there is no scoring, no match timer, and the reset that happens after
a goal is incomplete. That's what Tasks 2-4 fix/add.
"""

import math  # ADDED (Task 3): for rounding the countdown up
import random
import time  # ADDED (Task 3): real-time clock for the match timer

from game.puck import Puck
from game.paddle import Paddle
from game.ai import ComputerAI
from game.collisions import handle_paddle_collision
from game.renderer import WIDTH, HEIGHT, MARGIN, GOAL_TOP, GOAL_BOTTOM

PLAYER_SPEED = 6
PUCK_RADIUS = 12
PADDLE_RADIUS = 28
INITIAL_PUCK_SPEED = 4.5
MATCH_DURATION = 30  # ADDED (Task 3): match length in seconds


class GameEngine:
    def __init__(self):
        self.puck = Puck(WIDTH / 2, HEIGHT / 2, PUCK_RADIUS)
        self._launch_puck()

        self.player = Paddle(
            x=WIDTH * 0.15, y=HEIGHT / 2, radius=PADDLE_RADIUS,
            min_x=MARGIN + PADDLE_RADIUS, max_x=WIDTH / 2 - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS, max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )
        self.computer = Paddle(
            x=WIDTH * 0.85, y=HEIGHT / 2, radius=PADDLE_RADIUS,
            min_x=WIDTH / 2 + PADDLE_RADIUS, max_x=WIDTH - MARGIN - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS, max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )
        self.ai = ComputerAI()

        # ADDED (Task 2): match scores
        self.player_score = 0
        self.computer_score = 0
        # ADDED (Task 2): True once the match timer runs out (set in Task 3)
        self.match_over = False

        # ADDED (Task 3): match timer state
        self._start_time = time.monotonic()
        self.time_left = float(MATCH_DURATION)

    def _launch_puck(self):
        angle_choices = [0.3, 0.6, -0.3, -0.6]
        direction = random.choice([-1, 1])
        vy_factor = random.choice(angle_choices)
        self.puck.vx = INITIAL_PUCK_SPEED * direction
        self.puck.vy = INITIAL_PUCK_SPEED * vy_factor

    def handle_input(self, keys_pressed):
        # ADDED (Task 3): ignore input once the match has ended
        if self.match_over:
            return
        import pygame
        dx = dy = 0
        if keys_pressed[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        if keys_pressed[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        self.player.move_by(dx, dy)

    def update(self):
        # ADDED (Task 3): stop all game logic once the match is over
        if self.match_over:
            return

        # ADDED (Task 3): update the countdown from real elapsed time
        elapsed = time.monotonic() - self._start_time
        self.time_left = max(0.0, MATCH_DURATION - elapsed)
        if self.time_left <= 0:
            self.match_over = True
            return

        self.ai.update(self.computer, self.puck)

        # ADDED (Task 1): record this frame's paddle velocities before colliding
        self.player.update_velocity()
        self.computer.update_velocity()

        self.puck.move()
        self.puck.bounce_off_walls(HEIGHT, MARGIN)

        # CHANGED (Task 1): pass the puck-centre y limits to the collision handler
        min_y = MARGIN + PUCK_RADIUS
        max_y = HEIGHT - MARGIN - PUCK_RADIUS
        handle_paddle_collision(self.puck, self.player, min_y, max_y)
        handle_paddle_collision(self.puck, self.computer, min_y, max_y)

        self._handle_goals()

    def _handle_goals(self):
        # CHANGED (Task 2): a goal counts only when the puck is fully inside
        # the goal gap and has fully crossed the goal line.
        r = self.puck.radius
        in_gap = GOAL_TOP + r <= self.puck.y <= GOAL_BOTTOM - r

        if self.puck.x - r < MARGIN:
            if in_gap:
                if self.puck.x + r < MARGIN:
                    # ADDED (Task 2): puck in the left goal -> computer scores
                    self.computer_score += 1
                    self._reset_puck()
            else:
                self.puck.x = MARGIN + r
                self.puck.vx = -self.puck.vx
        elif self.puck.x + r > WIDTH - MARGIN:
            if in_gap:
                if self.puck.x - r > WIDTH - MARGIN:
                    # ADDED (Task 2): puck in the right goal -> player scores
                    self.player_score += 1
                    self._reset_puck()
            else:
                self.puck.x = WIDTH - MARGIN - r
                self.puck.vx = -self.puck.vx

    def _reset_puck(self):
        self.puck.x, self.puck.y = WIDTH / 2, HEIGHT / 2
        # CHANGED (Task 4): the old code set vx = vy = 0 here, which left the
        # puck frozen. Relaunch it instead: _launch_puck overwrites both
        # velocity components, so nothing from the goal shot carries over.
        self._launch_puck()

    # ADDED (Task 2): result of the match based on the current scores
    def winner_text(self):
        if self.player_score > self.computer_score:
            return "You win!"
        if self.computer_score > self.player_score:
            return "Computer wins!"
        return "Draw"

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_table(surface)
        renderer.draw_paddle(surface, self.player, renderer.COLOR_PLAYER)
        renderer.draw_paddle(surface, self.computer, renderer.COLOR_COMPUTER)
        renderer.draw_puck(surface, self.puck)

        # ADDED (Task 2): score display, one on each side of the centre line
        you_text = f"You {self.player_score}"
        cpu_text = f"Computer {self.computer_score}"
        text_y = MARGIN + 6
        renderer.draw_text(surface, font, you_text,
                           (WIDTH / 2 - 20 - font.size(you_text)[0], text_y),
                           renderer.COLOR_PLAYER)
        renderer.draw_text(surface, font, cpu_text,
                           (WIDTH / 2 + 20, text_y),
                           renderer.COLOR_COMPUTER)

        # ADDED (Task 3): remaining time, bottom centre
        timer_text = f"Time {math.ceil(self.time_left)}"
        renderer.draw_text(surface, font, timer_text,
                           (WIDTH / 2 - font.size(timer_text)[0] / 2,
                            HEIGHT - MARGIN - font.get_height() - 6))

        # ADDED (Task 2/3): winner banner, shown once the timer has run out
        if self.match_over:
            renderer.draw_banner(surface, font, self.winner_text())