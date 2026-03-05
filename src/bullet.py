import pygame
import os
from src.settings import HEIGHT
from src.gfx      import make_glow_surf


class Bullet(pygame.sprite.Sprite):
    SPEED = 14   # pixels per frame, going DOWN toward items

    def __init__(self, cx, top_y):
        super().__init__()
        self.image = self._make_bolt()
        self.rect  = self.image.get_rect()
        self.rect.centerx = cx
        self.rect.top     = top_y   # starts at bottom of player

        # pre-built glow so we don't rebuild every frame
        self._glow = make_glow_surf(self.image.get_width(),
                                    self.image.get_height(),
                                    (80, 200, 255), radius=12)

    def _make_bolt(self):
        """Glowing cyan energy bolt drawn procedurally."""
        w, h = 8, 32
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # outer soft glow
        pygame.draw.rect(surf, (20, 100, 200, 80),  (0, 0, w, h), border_radius=4)
        # mid glow
        pygame.draw.rect(surf, (80, 180, 255, 160), (1, 2, w-2, h-4), border_radius=3)
        # bright core
        pygame.draw.rect(surf, (200, 230, 255, 230), (2, 4, w-4, h-8), border_radius=2)
        # white hot center
        pygame.draw.rect(surf, (255, 255, 255, 255), (3, 6, w-6, h-12))
        # bright tip (pointed end at bottom = direction of travel)
        pygame.draw.rect(surf, (255, 255, 255), (3, h-8, 2, 6))
        return surf

    def update(self):
        self.rect.y += self.SPEED
        if self.rect.top > HEIGHT:
            self.kill()

    def draw_custom(self, surface):
        """Draw with glow - call this instead of using group.draw()."""
        gx = self.rect.centerx - self._glow.get_width()  // 2
        gy = self.rect.centery - self._glow.get_height() // 2
        surface.blit(self._glow, (gx, gy))
        surface.blit(self.image, self.rect)
