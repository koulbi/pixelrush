"""PIXELRUSH — game entry point."""
import pygame

from config import FPS, HEIGHT, TITLE, WIDTH
from game import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game = Game(screen)

    while game.running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            game.handle_event(event)
            if not game.running:
                break
        if not game.running:
            break
        game.update(dt)
        game.draw(game.screen)
        pygame.display.flip()

    game.shutdown()
    pygame.quit()


if __name__ == "__main__":
    main()
