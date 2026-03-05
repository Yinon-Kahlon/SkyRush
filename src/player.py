import pygame
import math
import random
import os
from src.settings import WIDTH, HEIGHT, PLAYER_SPEED, ASSET_IMG
from src.gfx      import make_glow_surf

SHIP_SIZE = 82   # bigger = more impressive on screen


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        ship_path = os.path.join(ASSET_IMG, "player", "ship.png")
        try:
            raw = pygame.image.load(ship_path).convert_alpha()
            self.original_image = pygame.transform.scale(raw, (SHIP_SIZE, SHIP_SIZE))
        except Exception as e:
            print(f"Ship sprite not found ({e}), using placeholder")
            self.original_image = self._draw_placeholder()

        # pre-build glow surface (static, just redrawn at tilt)
        self._glow = make_glow_surf(SHIP_SIZE, SHIP_SIZE, (0, 140, 255), radius=22)

        self.image = self.original_image.copy()
        self.rect  = self.image.get_rect()

        self.rect.centerx = WIDTH  // 2
        self.rect.centery  = 95

        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

        self.tilt      = 0.0
        self.invincible = False
        self.inv_timer  = 0
        self.INV_FRAMES = 90

        self.flame_timer = 0
        self._trail = []   # list of (x, y, alpha) for engine trail

    # ── placeholder ship ──────────────────────────────────────────────────────

    def _draw_placeholder(self):
        surf   = pygame.Surface((SHIP_SIZE, SHIP_SIZE), pygame.SRCALPHA)
        pts    = [(SHIP_SIZE//2, 4),
                  (SHIP_SIZE-8,  SHIP_SIZE-8),
                  (SHIP_SIZE//2, SHIP_SIZE-20),
                  (8,            SHIP_SIZE-8)]
        pygame.draw.polygon(surf, (20, 140, 255), pts)
        pygame.draw.polygon(surf, (150, 220, 255), pts, 2)
        # cockpit
        pygame.draw.circle(surf, (200, 240, 255), (SHIP_SIZE//2, SHIP_SIZE//3), 8)
        return surf

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, keys):
        dx, dy = 0, 0

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += PLAYER_SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += PLAYER_SPEED

        # diagonal normalization
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.fx += dx
        self.fy += dy
        self.fx = max(6, min(WIDTH  - SHIP_SIZE - 6, self.fx))
        self.fy = max(6, min(HEIGHT - SHIP_SIZE - 6, self.fy))

        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

        # smooth tilt
        target = dx * 3.2
        self.tilt += (target - self.tilt) * 0.16
        self.tilt  = max(-28.0, min(28.0, self.tilt))

        if abs(self.tilt) > 0.4:
            self.image  = pygame.transform.rotate(self.original_image, -self.tilt)
            center      = self.rect.center
            self.rect   = self.image.get_rect(center=center)
        else:
            self.image  = self.original_image

        if self.invincible:
            self.inv_timer -= 1
            if self.inv_timer <= 0:
                self.invincible = False

        self.flame_timer += 1

        # record trail points
        self._trail.append((self.rect.centerx, self.rect.bottom - 6, 180))
        if len(self._trail) > 18:
            self._trail.pop(0)

    def take_hit(self):
        if not self.invincible:
            self.invincible = True
            self.inv_timer  = self.INV_FRAMES
            return True
        return False

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface):
        # always draw engine effects (even when flashing)
        self._draw_engine_trail(surface)
        self._draw_engine_flame(surface)

        if self.invincible and (self.inv_timer // 5) % 2 == 0:
            return  # flash effect

        # glow halo behind the ship
        gx = self.rect.centerx - self._glow.get_width()  // 2
        gy = self.rect.centery - self._glow.get_height() // 2
        surface.blit(self._glow, (gx, gy))

        surface.blit(self.image, self.rect)

    def _draw_engine_flame(self, surface):
        """Multi-nozzle animated flame."""
        ft     = self.flame_timer
        flick  = 0.5 + 0.5 * math.sin(ft * 0.6)
        cx     = self.rect.centerx
        cy     = self.rect.bottom - 6

        # main center nozzle
        self._flame_nozzle(surface, cx, cy, 18, flick)
        # two side nozzles
        self._flame_nozzle(surface, cx - 18, cy - 4, 10, flick * 0.8)
        self._flame_nozzle(surface, cx + 18, cy - 4, 10, flick * 0.8)

    def _flame_nozzle(self, surface, cx, cy, width, flicker):
        h     = int((14 + flicker * 22))
        flame = pygame.Surface((width + 4, h + 4), pygame.SRCALPHA)
        hw    = (width + 4) // 2
        for i in range(h):
            t     = i / max(1, h)
            alpha = int(240 * (1 - t) ** 1.4)
            # inner white → yellow → orange
            if t < 0.25:
                c = (255, 255, int(200 * (1-t*4)))
            elif t < 0.6:
                c = (255, int(200 * (1 - (t-0.25)/0.35)), 0)
            else:
                c = (int(255 * (1 - (t-0.6)/0.4)), 0, 0)
            flame.set_at((hw, i), (*c, alpha))
            if i > 2:
                flame.set_at((hw-1, i), (*c, alpha//2))
                flame.set_at((hw+1, i), (*c, alpha//2))
        surface.blit(flame, (cx - hw, cy))

    def _draw_engine_trail(self, surface):
        """Faint blue ghost trail."""
        for idx, (tx, ty, a_base) in enumerate(self._trail):
            alpha  = int(a_base * (idx / len(self._trail)) * 0.5)
            radius = max(1, 3 - (len(self._trail) - idx) // 6)
            dot    = pygame.Surface((radius*2+1, radius*2+1), pygame.SRCALPHA)
            pygame.draw.circle(dot, (80, 160, 255, alpha), (radius, radius), radius)
            surface.blit(dot, (tx - radius, ty - radius))
