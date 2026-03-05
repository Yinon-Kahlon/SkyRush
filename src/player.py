import pygame
import os
from src.settings import WIDTH, HEIGHT, PLAYER_SPEED, ASSET_IMG

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # load ship sprite from Kenney pack
        ship_path = os.path.join(ASSET_IMG, "player", "ship.png")
        try:
            raw = pygame.image.load(ship_path).convert_alpha()
            self.original_image = pygame.transform.scale(raw, (64, 64))
        except Exception as e:
            print(f"Ship image load failed: {e}, using placeholder")
            self.original_image = self._draw_placeholder()

        self.image = self.original_image.copy()
        self.rect  = self.image.get_rect()

        # start near the top center
        self.rect.centerx = WIDTH // 2
        self.rect.centery  = 90

        # use floats for smooth movement
        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

        # tilt effect
        self.tilt = 0.0

        # invincibility after getting hit
        self.invincible  = False
        self.inv_timer   = 0
        self.INV_FRAMES  = 90   # 1.5 sec at 60fps

        # engine flame animation
        self.flame_timer = 0

    def _draw_placeholder(self):
        # basic triangle ship if sprite fails to load
        surf   = pygame.Surface((60, 60), pygame.SRCALPHA)
        points = [(30, 4), (56, 56), (30, 44), (4, 56)]
        pygame.draw.polygon(surf, (0, 160, 255), points)
        pygame.draw.polygon(surf, (180, 230, 255), points, 2)
        return surf

    def update(self, keys):
        dx, dy = 0, 0

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += PLAYER_SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += PLAYER_SPEED

        # fix diagonal speed (classic fix every student uses)
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.fx += dx
        self.fy += dy

        # clamp inside screen (leave some margin so ship doesn't half-disappear)
        self.fx = max(5, min(WIDTH  - self.rect.width  - 5, self.fx))
        self.fy = max(5, min(HEIGHT - self.rect.height - 5, self.fy))

        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

        # tilt - smoothly follow horizontal movement
        target_tilt  = dx * 3.5
        self.tilt   += (target_tilt - self.tilt) * 0.18
        self.tilt    = max(-25.0, min(25.0, self.tilt))

        # apply tilt to the image
        if abs(self.tilt) > 0.5:
            self.image = pygame.transform.rotate(self.original_image, -self.tilt)
            center     = self.rect.center
            self.rect  = self.image.get_rect(center=center)
        else:
            self.image = self.original_image

        # invincibility countdown
        if self.invincible:
            self.inv_timer -= 1
            if self.inv_timer <= 0:
                self.invincible = False

        self.flame_timer += 1

    def take_hit(self):
        # returns True if hit actually registered (not already invincible)
        if not self.invincible:
            self.invincible = True
            self.inv_timer  = self.INV_FRAMES
            return True
        return False

    def draw(self, surface):
        # flash effect while invincible
        if self.invincible and (self.inv_timer // 5) % 2 == 0:
            return

        surface.blit(self.image, self.rect)

        # draw little engine flames when moving (nice touch)
        self._draw_engine_flame(surface)

    def _draw_engine_flame(self, surface):
        # just a small orange/yellow flicker below the ship
        cx = self.rect.centerx
        cy = self.rect.bottom - 4
        flicker = abs(pygame.math.Vector2(0, 1).rotate(self.flame_timer * 15).y)
        h = int(10 + flicker * 8)

        flame_surf = pygame.Surface((14, h + 4), pygame.SRCALPHA)
        for i in range(h):
            alpha = int(200 * (1 - i / h))
            color  = (255, max(0, 160 - i * 8), 0, alpha)
            pygame.draw.line(flame_surf, color, (7, i), (7, i))
        surface.blit(flame_surf, (cx - 7, cy))
