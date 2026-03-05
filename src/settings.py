# settings.py - all constants in one place, easy to tweak

WIDTH  = 800
HEIGHT = 600
FPS    = 60
TITLE  = "SkyRush"

# player
PLAYER_SPEED      = 6
PLAYER_START_LIVES = 3

# items
ITEM_BASE_SPEED   = 2.5
SPEED_PER_LEVEL   = 0.6    # added each level
ITEMS_PER_LEVEL   = 10     # good items needed to level up

# spawn timers (in frames) - go up/down as level increases
GOOD_SPAWN_BASE   = 55
BAD_SPAWN_BASE    = 75
GOOD_SPAWN_INC    = 8      # less good items each level
BAD_SPAWN_DEC     = 10     # more bad items each level
MIN_SPAWN_RATE    = 20     # don't let it go below this

# score
STAR_SCORE        = 1
BOLT_SCORE        = 3

# colors
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
YELLOW     = (255, 220, 0)
RED        = (220, 50,  50)
GREEN      = (80,  220, 100)
CYAN       = (0,   200, 255)
PURPLE     = (150, 50,  220)
ORANGE     = (255, 140, 0)
DARK_BLUE  = (5,   5,   25)
GREY       = (120, 120, 140)
LIGHT_BLUE = (100, 180, 255)

# paths (relative to project root)
import os
ROOT       = os.path.join(os.path.dirname(__file__), "..")
ASSET_IMG  = os.path.join(ROOT, "assets", "images")
ASSET_SND  = os.path.join(ROOT, "assets", "sounds")
ASSET_FONT = os.path.join(ROOT, "assets", "fonts")
