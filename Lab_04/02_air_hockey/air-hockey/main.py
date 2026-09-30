"""
Air Hockey (Lab Starter)

Run with:  python3 main.py

Controls: Arrow keys move your paddle (left side, blue).
          R restarts the match at any time.
"""

import pygame

from game.game_engine import GameEngine
from game.renderer import WINDOW_SIZE


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Air Hockey")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)

    engine = GameEngine()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # ADDED: press R at any time to restart (fresh scores, timer, puck, paddles)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                engine = GameEngine()

        keys = pygame.key.get_pressed()
        engine.handle_input(keys)
        engine.update()
        engine.draw(screen, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()