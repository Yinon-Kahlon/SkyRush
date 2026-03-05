# settings.py - all constants in one place, easy to tweak

WIDTH  = 800
HEIGHT = 600
FPS    = 60
TITLE  = "SkyRush"

# player
PLAYER_SPEED      = 6
PLAYER_START_LIVES = 3

# items  (SpawnController manages these dynamically, these are starting values)
ITEM_BASE_SPEED   = 3.2
SPEED_PER_LEVEL   = 0.75   # added each level-up
ITEMS_PER_LEVEL   = 8      # good items needed to level up

# spawn timers (in frames) - SpawnController adjusts these as level increases
GOOD_SPAWN_BASE   = 52
BAD_SPAWN_BASE    = 68
GOOD_SPAWN_INC    = 5      # interval grows each level (fewer good items)
BAD_SPAWN_DEC     = 8      # interval shrinks each level (more bad items)
MIN_SPAWN_RATE    = 20     # hard floor - don't go below this

# score
STAR_SCORE        = 100
BOLT_SCORE        = 100

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
