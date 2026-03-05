import pygame
import random
import os
from src.settings import WIDTH, HEIGHT, STAR_SCORE, BOLT_SCORE, ASSET_IMG


# ─── Base ─────────────────────────────────────────────────────────────────────

class Item(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.speed      = speed
        self.angle      = 0
        self.spin_speed = 0

    def update(self):
        self.rect.y -= self.speed
        if self.spin_speed != 0:
            self.angle = (self.angle + self.spin_speed) % 360
            self.image = pygame.transform.rotate(self.orig_image, self.angle)
            center     = self.rect.center
            self.rect  = self.image.get_rect(center=center)
        if self.rect.bottom < 0:
            self.kill()


# ─── Good items ───────────────────────────────────────────────────────────────

class GoodItem(Item):
    def __init__(self, speed, item_type=None):
        super().__init__(speed)
        if item_type is None:
            item_type = random.choice([1, 1, 1, 2])
        self.item_type = item_type
        self.score_val = STAR_SCORE if item_type == 1 else BOLT_SCORE

        img_path = os.path.join(ASSET_IMG, "items",
                                "good_item.png" if item_type == 1 else "good_item2.png")
        try:
            raw             = pygame.image.load(img_path).convert_alpha()
            size            = 40 if item_type == 1 else 44
            self.orig_image = pygame.transform.scale(raw, (size, size))
        except:
            self.orig_image = self._make_fallback(item_type)

        self.image      = self.orig_image.copy()
        self.rect       = self.image.get_rect()
        self.rect.x     = random.randint(20, WIDTH - 60)
        self.rect.y     = HEIGHT + random.randint(10, 40)
        self.spin_speed = 2.5 if item_type == 1 else 1.8

    def _make_fallback(self, t):
        surf = pygame.Surface((36, 36), pygame.SRCALPHA)
        if t == 1:
            pygame.draw.circle(surf, (255, 220, 0),   (18, 18), 14)
            pygame.draw.circle(surf, (255, 255, 150),  (18, 18), 7)
        else:
            pts = [(18,2),(30,16),(22,16),(26,34),(8,18),(16,18)]
            pygame.draw.polygon(surf, (0, 210, 255), pts)
        return surf

    def get_glow_color(self):
        return (255, 220, 0) if self.item_type == 1 else (0, 200, 255)


# ─── Bad items ────────────────────────────────────────────────────────────────

class BadItem(Item):
    def __init__(self, speed, item_type=None):
        super().__init__(speed)
        if item_type is None:
            item_type = random.choice([1, 1, 2])
        self.item_type = item_type

        img_path = os.path.join(ASSET_IMG, "items",
                                "bad_item.png" if item_type == 1 else "bad_item2.png")
        try:
            raw             = pygame.image.load(img_path).convert_alpha()
            size            = 54 if item_type == 1 else 50
            self.orig_image = pygame.transform.scale(raw, (size, size))
        except:
            self.orig_image = self._make_fallback(item_type)

        self.spin_speed = 1.2 if item_type == 1 else 0.0
        if item_type == 2:
            self.orig_image = pygame.transform.flip(self.orig_image, False, True)

        self.image  = self.orig_image.copy()
        self.rect   = self.image.get_rect()
        self.rect.x = random.randint(20, WIDTH - 70)
        self.rect.y = HEIGHT + random.randint(10, 60)
        self.drift  = random.uniform(-0.6, 0.6) if item_type == 2 else 0.0

    def _make_fallback(self, t):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        if t == 1:
            pygame.draw.circle(surf, (140, 90, 50), (24, 24), 22)
            pygame.draw.circle(surf, (100, 65, 35), (24, 24), 22, 3)
            pygame.draw.circle(surf, (80,  50, 25), (14, 18), 6)
        else:
            pygame.draw.polygon(surf, (200, 30, 30), [(24,4),(44,44),(24,36),(4,44)])
        return surf

    def update(self):
        self.rect.x += self.drift
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.drift *= -1
        super().update()

    def get_glow_color(self):
        return (220, 50, 50)


# ─── Rush wave item  (fast meteor burst) ─────────────────────────────────────

class RushItem(BadItem):
    """Faster-than-normal bad item used during wave rushes."""
    def __init__(self, base_speed):
        speed = base_speed * random.uniform(1.3, 1.8)
        super().__init__(speed, item_type=1)
        self.spin_speed *= 2.0   # spins faster too, looks chaotic


# ─── SpawnController ─────────────────────────────────────────────────────────

class SpawnController:
    """
    Manages item spawning and difficulty scaling.
    Two axes of difficulty:
      1. Score-based level ups (every 8 good items caught)
      2. Time-based slow pressure (every 8 seconds, independent of score)
    Plus rush waves at higher levels.
    """

    def __init__(self):
        self.level = 1

        # base speed — screen is 600px tall, so speed=4 → item crosses in ~2.5s
        self.item_speed    = 3.2
        self.good_timer    = 0
        self.bad_timer     = 0
        self.good_interval = 52   # frames between good spawns
        self.bad_interval  = 68   # frames between bad spawns
        self.good_collected = 0

        # time pressure (independent of score)
        self.frame_count   = 0
        self.TIME_SCALE_EVERY = 480   # every 8 seconds at 60fps

        # rush waves
        self.rush_timer    = 0
        self.rush_every    = 1800     # every 30s at first
        self.rush_count    = 3        # how many rush items per wave

    def update(self):
        new_items = []
        self.frame_count += 1
        self.good_timer  += 1
        self.bad_timer   += 1
        self.rush_timer  += 1

        # ── normal spawns ────────────────────────────────────────────────────
        if self.good_timer >= self.good_interval:
            self.good_timer = 0
            new_items.append(GoodItem(self.item_speed))

        if self.bad_timer >= self.bad_interval:
            self.bad_timer = 0
            new_items.append(BadItem(self.item_speed))

            # double-spawn at level 4+ (30% chance)
            if self.level >= 4 and random.random() < 0.30:
                offset = random.randint(-180, 180)   # stagger x so they don't overlap
                extra  = BadItem(self.item_speed * random.uniform(0.9, 1.1))
                extra.rect.x = max(20, min(WIDTH-70, extra.rect.x + offset))
                new_items.append(extra)

            # triple-spawn at level 7+ (20% chance)
            if self.level >= 7 and random.random() < 0.20:
                new_items.append(BadItem(self.item_speed * 1.15))

        # ── rush wave ────────────────────────────────────────────────────────
        if self.level >= 3 and self.rush_timer >= self.rush_every:
            self.rush_timer = 0
            for i in range(self.rush_count):
                ri = RushItem(self.item_speed)
                ri.rect.x = random.randint(20, WIDTH - 70)
                ri.rect.y = HEIGHT + i * 40   # stagger so they don't arrive all at once
                new_items.append(ri)

        # ── time-based pressure ──────────────────────────────────────────────
        if self.frame_count % self.TIME_SCALE_EVERY == 0:
            self._time_pressure()

        return new_items

    def _time_pressure(self):
        """Slow creep even if player doesn't collect items."""
        self.item_speed   = min(16.0, self.item_speed + 0.18)
        self.bad_interval = max(20, self.bad_interval - 2)

    def on_good_collected(self):
        self.good_collected += 1
        if self.good_collected % 8 == 0:   # level up every 8 catches (was 10)
            return self._level_up()
        return False

    def _level_up(self):
        self.level      += 1
        self.item_speed  = min(16.0, self.item_speed + 0.75)

        # good items scarcer
        self.good_interval = max(18, self.good_interval + 5)
        # bad items more frequent
        self.bad_interval  = max(20, self.bad_interval - 8)

        # rush waves become more frequent and bigger
        self.rush_every  = max(900, self.rush_every - 120)   # min every 15s
        self.rush_count  = min(8,   self.rush_count + 1)

        return True
