import pygame
import random
import os
from src.settings import WIDTH, HEIGHT, STAR_SCORE, BOLT_SCORE, ASSET_IMG

# base class for both item types
class Item(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.speed       = speed
        self.angle       = 0
        self.spin_speed  = 0   # set by subclasses

    def update(self):
        self.rect.y -= self.speed

        # spin the item as it rises
        if self.spin_speed != 0:
            self.angle = (self.angle + self.spin_speed) % 360
            self.image = pygame.transform.rotate(self.orig_image, self.angle)
            center     = self.rect.center
            self.rect  = self.image.get_rect(center=center)

        # remove once it's fully off screen
        if self.rect.bottom < 0:
            self.kill()


class GoodItem(Item):
    def __init__(self, speed, item_type=None):
        super().__init__(speed)

        # randomly pick type 1 (star +1) or type 2 (bolt +3)
        if item_type is None:
            item_type = random.choice([1, 1, 1, 2])   # stars are more common
        self.item_type  = item_type
        self.score_val  = STAR_SCORE if item_type == 1 else BOLT_SCORE

        # load matching sprite
        if item_type == 1:
            img_path = os.path.join(ASSET_IMG, "items", "good_item.png")
        else:
            img_path = os.path.join(ASSET_IMG, "items", "good_item2.png")

        try:
            raw            = pygame.image.load(img_path).convert_alpha()
            size           = 38 if item_type == 1 else 42
            self.orig_image = pygame.transform.scale(raw, (size, size))
        except:
            self.orig_image = self._make_fallback(item_type)

        self.image      = self.orig_image.copy()
        self.rect       = self.image.get_rect()
        self.rect.x     = random.randint(20, WIDTH - 60)
        self.rect.y     = HEIGHT + random.randint(10, 40)  # just below screen

        self.spin_speed = 2.5 if item_type == 1 else 1.8

    def _make_fallback(self, item_type):
        surf = pygame.Surface((36, 36), pygame.SRCALPHA)
        if item_type == 1:
            # yellow star shape
            pygame.draw.circle(surf, (255, 220, 0), (18, 18), 14)
            pygame.draw.circle(surf, (255, 255, 150), (18, 18), 7)
        else:
            # cyan bolt
            pts = [(18, 2), (30, 16), (22, 16), (26, 34), (8, 18), (16, 18)]
            pygame.draw.polygon(surf, (0, 210, 255), pts)
        return surf

    # glow tint to show value difference
    def get_glow_color(self):
        return (255, 220, 0) if self.item_type == 1 else (0, 200, 255)


class BadItem(Item):
    def __init__(self, speed, item_type=None):
        super().__init__(speed)

        if item_type is None:
            item_type = random.choice([1, 1, 2])   # meteors more common than ships

        self.item_type = item_type

        if item_type == 1:
            img_path = os.path.join(ASSET_IMG, "items", "bad_item.png")
        else:
            img_path = os.path.join(ASSET_IMG, "items", "bad_item2.png")

        try:
            raw             = pygame.image.load(img_path).convert_alpha()
            size            = 52 if item_type == 1 else 48
            self.orig_image  = pygame.transform.scale(raw, (size, size))
        except:
            self.orig_image  = self._make_fallback(item_type)

        # enemy ships don't spin (they're ships, not rocks)
        self.spin_speed = 1.2 if item_type == 1 else 0.0
        if item_type == 2:
            # flip enemy ship so it faces downward (toward player, coming from below)
            self.orig_image = pygame.transform.flip(self.orig_image, False, True)

        self.image  = self.orig_image.copy()
        self.rect   = self.image.get_rect()
        self.rect.x = random.randint(20, WIDTH - 70)
        self.rect.y = HEIGHT + random.randint(10, 60)

        # slight horizontal drift for enemy ships
        self.drift  = random.uniform(-0.5, 0.5) if item_type == 2 else 0.0

    def _make_fallback(self, item_type):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        if item_type == 1:
            # brown-ish rock shape
            pygame.draw.circle(surf, (140, 90, 50), (24, 24), 22)
            pygame.draw.circle(surf, (100, 65, 35), (24, 24), 22, 3)
            pygame.draw.circle(surf, (80, 50, 25), (14, 18), 6)
            pygame.draw.circle(surf, (80, 50, 25), (30, 30), 4)
        else:
            # red enemy ship
            pts = [(24, 4), (44, 44), (24, 36), (4, 44)]
            pygame.draw.polygon(surf, (200, 30, 30), pts)
        return surf

    def update(self):
        # horizontal drift for enemy ships
        self.rect.x += self.drift
        # bounce off screen sides
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.drift *= -1
        super().update()

    def get_glow_color(self):
        return (220, 50, 50)


# ─── Level / spawn controller ────────────────────────────────────────────────

class SpawnController:
    """
    Handles spawn timing and level progression.
    Keeps track of when to spawn items and adjusts difficulty.
    """
    def __init__(self):
        self.level          = 1
        self.item_speed     = 2.5
        self.good_timer     = 0
        self.bad_timer      = 0
        self.good_interval  = 55   # frames between good item spawns
        self.bad_interval   = 75
        self.good_collected = 0    # total good items caught

    def update(self):
        """Returns a list of new items to spawn this frame (can be empty)."""
        new_items = []

        self.good_timer += 1
        self.bad_timer  += 1

        if self.good_timer >= self.good_interval:
            self.good_timer = 0
            new_items.append(GoodItem(self.item_speed))

        if self.bad_timer >= self.bad_interval:
            self.bad_timer = 0
            new_items.append(BadItem(self.item_speed))

        return new_items

    def on_good_collected(self):
        """Call when player picks up a good item."""
        self.good_collected += 1
        if self.good_collected % 10 == 0:
            return self.level_up()
        return False

    def level_up(self):
        self.level         += 1
        self.item_speed    += 0.6
        # good items appear less often
        self.good_interval  = max(20, self.good_interval + 8)
        # bad items appear more often
        self.bad_interval   = max(20, self.bad_interval  - 10)
        return True   # signal: level changed
