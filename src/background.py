import pygame
import random
import os
from src.settings import WIDTH, HEIGHT, ASSET_IMG

# handles the scrolling star field background
# using 3 layers for a parallax effect - looks way better than a static image

class Background:
    def __init__(self):
        # try to load the downloaded space image
        self.bg_image = None
        bg_path = os.path.join(ASSET_IMG, "backgrounds", "space_bg.jpg")
        if os.path.exists(bg_path) and os.path.getsize(bg_path) > 5000:
            try:
                img = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.scale(img, (WIDTH, HEIGHT))
            except:
                pass  # just use the star field then

        # generate star layers regardless (drawn on top of bg or alone)
        # layer 0 = farthest (slow, small, dim)
        # layer 2 = closest (fast, big, bright)
        self.layers = [
            self._make_stars(120, 1, (80, 80, 110)),
            self._make_stars(70,  2, (140, 140, 180)),
            self._make_stars(30,  3, (220, 220, 255)),
        ]
        self.speeds  = [0.3, 0.7, 1.4]
        self.offsets = [0.0, 0.0, 0.0]

        # some bigger "nebula" blobs for atmosphere (only if no bg image)
        if not self.bg_image:
            self.nebula_surf = self._make_nebula()
        else:
            self.nebula_surf = None

    def _make_stars(self, count, size, color):
        surf = pygame.Surface((WIDTH, HEIGHT * 2), pygame.SRCALPHA)
        for _ in range(count):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT * 2)
            # tiny variation in brightness
            brightness = random.randint(160, 255)
            c = tuple(min(255, int(ch * brightness / 255)) for ch in color)
            pygame.draw.circle(surf, c, (x, y), size)
            # add a soft glow around bigger stars
            if size >= 2:
                glow = pygame.Surface((size * 6, size * 6), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*c, 40), (size * 3, size * 3), size * 3)
                surf.blit(glow, (x - size * 3, y - size * 3))
        return surf

    def _make_nebula(self):
        # draw some colorful blobs to fake a nebula
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        blobs = [
            (200, 150, (20, 0, 60,  35), 180),
            (550, 300, (0,  20, 80, 30), 200),
            (350, 400, (40, 0, 50,  25), 150),
        ]
        for bx, by, color, r in blobs:
            blob = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(blob, color, (r, r), r)
            surf.blit(blob, (bx - r, by - r), special_flags=pygame.BLEND_RGBA_ADD)
        return surf

    def update(self):
        for i in range(len(self.layers)):
            self.offsets[i] = (self.offsets[i] + self.speeds[i]) % HEIGHT

    def draw(self, surface):
        # base - either downloaded image or dark background
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((5, 5, 25))
            if self.nebula_surf:
                surface.blit(self.nebula_surf, (0, 0))

        # draw each star layer with scrolling offset (loop seamlessly)
        for i, layer in enumerate(self.layers):
            offset = int(self.offsets[i])
            # draw the layer twice to get seamless loop
            surface.blit(layer, (0, offset - HEIGHT))
            surface.blit(layer, (0, offset))
