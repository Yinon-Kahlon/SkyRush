import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.settings import WIDTH, HEIGHT, TITLE
from src.game     import Game

def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # set window icon (using the ship sprite if available)
    icon_path = os.path.join("assets", "images", "player", "ship.png")
    if os.path.exists(icon_path):
        try:
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
        except:
            pass

    game = Game(screen)
    game.run()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
