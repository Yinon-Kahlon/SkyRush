import pygame
import math
import os
from src.settings import WIDTH, HEIGHT, PLAYER_SPEED, ASSET_IMG
from src.gfx      import make_glow_surf

SHIP_SIZE     = 82
SHOOT_COOLDOWN = 18   # frames between shots (~0.3s at 60fps)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        ship_path = os.path.join(ASSET_IMG, "player", "ship.png")
        try:
            raw = pygame.image.load(ship_path).convert_alpha()
            scaled = pygame.transform.scale(raw, (SHIP_SIZE, SHIP_SIZE))
            # flip vertically so ship faces DOWN toward the enemies
            self.original_image = pygame.transform.flip(scaled, False, True)
        except Exception as e:
            print(f"Ship sprite error ({e}), placeholder used")
            self.original_image = self._draw_placeholder()

        self._glow  = make_glow_surf(SHIP_SIZE, SHIP_SIZE, (0, 140, 255), radius=22)
        self.image  = self.original_image.copy()
        self.rect   = self.image.get_rect()

        self.rect.centerx = WIDTH  // 2
        self.rect.centery  = 95

        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

        self.tilt       = 0.0
        self.invincible = False
        self.inv_timer  = 0
        self.INV_FRAMES = 90

        self.shoot_cooldown = 0   # counts down to 0 = ready to fire
        self.flame_timer    = 0
        self._trail         = []

    def _draw_placeholder(self):
        surf = pygame.Surface((SHIP_SIZE, SHIP_SIZE), pygame.SRCALPHA)
        # triangle pointing DOWN (toward enemies)
        pts = [(SHIP_SIZE//2, SHIP_SIZE-4),
               (SHIP_SIZE-8,  8),
               (SHIP_SIZE//2, 20),
               (8,            8)]
        pygame.draw.polygon(surf, (20, 140, 255), pts)
        pygame.draw.polygon(surf, (150, 220, 255), pts, 2)
        pygame.draw.circle(surf, (200, 240, 255),
                           (SHIP_SIZE//2, SHIP_SIZE * 2 // 3), 8)
        return surf

    # ─── update ───────────────────────────────────────────────────────────────

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += PLAYER_SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += PLAYER_SPEED

        if dx != 0 and dy != 0:
            dx *= 0.707; dy *= 0.707

        self.fx += dx;  self.fy += dy
        self.fx = max(6, min(WIDTH  - SHIP_SIZE - 6, self.fx))
        self.fy = max(6, min(HEIGHT - SHIP_SIZE - 6, self.fy))
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

        target = dx * 3.2
        self.tilt += (target - self.tilt) * 0.16
        self.tilt  = max(-28.0, min(28.0, self.tilt))

        if abs(self.tilt) > 0.4:
            self.image = pygame.transform.rotate(self.original_image, -self.tilt)
            center     = self.rect.center
            self.rect  = self.image.get_rect(center=center)
        else:
            self.image = self.original_image

        if self.invincible:
            self.inv_timer -= 1
            if self.inv_timer <= 0:
                self.invincible = False

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.flame_timer += 1

        # engine trail — comes from the TOP of the ship (engines after flip)
        self._trail.append((self.rect.centerx, self.rect.top + 6, 180))
        if len(self._trail) > 18:
            self._trail.pop(0)

    def try_shoot(self):
        """Returns (cx, y) if can shoot, else None. Called by game when SPACE held."""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            # bullet comes from the BOTTOM of the ship (nose = facing down)
            return (self.rect.centerx, self.rect.bottom)
        return None

    def take_hit(self):
        if not self.invincible:
            self.invincible = True
            self.inv_timer  = self.INV_FRAMES
            return True
        return False

    # ─── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface):
        self._draw_engine_trail(surface)
        self._draw_engine_flame(surface)

        if self.invincible and (self.inv_timer // 5) % 2 == 0:
            return

        gx = self.rect.centerx - self._glow.get_width()  // 2
        gy = self.rect.centery - self._glow.get_height() // 2
        surface.blit(self._glow, (gx, gy))
        surface.blit(self.image, self.rect)

    def _draw_engine_flame(self, surface):
        """Flames come from the TOP of the ship (engine end after vertical flip)."""
        ft    = self.flame_timer
        flick = 0.5 + 0.5 * math.sin(ft * 0.6)
        cx    = self.rect.centerx
        # after flip: engines are at TOP — flames go upward
        cy    = self.rect.top + 6

        self._flame_nozzle(surface, cx,      cy, 18, flick, upward=True)
        self._flame_nozzle(surface, cx - 18, cy - 4, 10, flick * 0.8, upward=True)
        self._flame_nozzle(surface, cx + 18, cy - 4, 10, flick * 0.8, upward=True)

    def _flame_nozzle(self, surface, cx, cy, width, flicker, upward=False):
        h   = int(14 + flicker * 22)
        hw  = (width + 4) // 2
        surf = pygame.Surface((width + 4, h + 4), pygame.SRCALPHA)
        for i in range(h):
            t     = i / max(1, h)
            alpha = int(240 * (1 - t) ** 1.4)
            if   t < 0.25: c = (255, 255, int(200 * (1 - t * 4)))
            elif t < 0.60: c = (255, int(200 * (1 - (t-0.25)/0.35)), 0)
            else:           c = (int(255 * (1 - (t-0.6)/0.4)), 0, 0)
            surf.set_at((hw, i), (*c, alpha))
            if i > 2:
                surf.set_at((hw-1, i), (*c, alpha//2))
                surf.set_at((hw+1, i), (*c, alpha//2))
        if upward:
            surf = pygame.transform.flip(surf, False, True)
            surface.blit(surf, (cx - hw, cy - h - 4))
        else:
            surface.blit(surf, (cx - hw, cy))

    def _draw_engine_trail(self, surface):
        for idx, (tx, ty, _) in enumerate(self._trail):
            alpha  = int(150 * (idx / max(1, len(self._trail))) * 0.5)
            radius = max(1, 3 - (len(self._trail) - idx) // 6)
            dot    = pygame.Surface((radius*2+1, radius*2+1), pygame.SRCALPHA)
            pygame.draw.circle(dot, (80, 160, 255, alpha), (radius, radius), radius)
            surface.blit(dot, (tx - radius, ty - radius))
