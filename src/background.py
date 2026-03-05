import pygame
import random
import math
from src.settings import WIDTH, HEIGHT


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _build_nebula():
    """
    Pre-renders a colorful space nebula using additive blending.
    Runs once at startup (~0.3s). Totally worth it.
    """
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((3, 4, 18))

    blob_surf = pygame.Surface((WIDTH, HEIGHT))
    blob_surf.fill((0, 0, 0))

    # each entry: (cx, cy, x_spread, y_spread, count, r_min, r_max, color_fn)
    regions = [
        # blue/teal - left
        (160, 300, 210, 180, 100, 40, 150,
         lambda: (random.randint(0,15), random.randint(20,80), random.randint(90,200))),
        # violet/purple - right
        (640, 230, 190, 160, 90, 35, 130,
         lambda: (random.randint(60,180), random.randint(0,30), random.randint(80,210))),
        # magenta - top center
        (400, 130, 170, 100, 55, 25, 95,
         lambda: (random.randint(110,220), random.randint(0,40), random.randint(80,170))),
        # cyan glow - bottom right
        (660, 500, 160, 120, 55, 20, 85,
         lambda: (random.randint(0,30), random.randint(90,200), random.randint(150,255))),
        # orange accent - bottom left
        (130, 490, 130, 100, 40, 20, 75,
         lambda: (random.randint(140,230), random.randint(40,90), random.randint(0,30))),
        # bright star-cluster core - center
        (400, 290, 90, 80, 30, 10, 50,
         lambda: (random.randint(180,255), random.randint(160,255), random.randint(100,220))),
        # second blue sweep
        (300, 450, 180, 130, 60, 30, 100,
         lambda: (random.randint(0,20), random.randint(40,130), random.randint(120,240))),
    ]

    for cx, cy, sx, sy, count, rmin, rmax, color_fn in regions:
        for _ in range(count):
            x = int(random.gauss(cx, sx))
            y = int(random.gauss(cy, sy))
            r = random.randint(rmin, rmax)
            c = color_fn()
            sc = random.uniform(0.04, 0.16)
            cs = (max(0, min(255, int(c[0]*sc))),
                  max(0, min(255, int(c[1]*sc))),
                  max(0, min(255, int(c[2]*sc))))
            tmp = pygame.Surface((r*2, r*2))
            tmp.fill((0, 0, 0))
            pygame.draw.circle(tmp, cs, (r, r), r)
            blob_surf.blit(tmp, (x-r, y-r), special_flags=pygame.BLEND_ADD)

    surf.blit(blob_surf, (0, 0), special_flags=pygame.BLEND_ADD)

    # slight brightness boost so colors aren't too muddy
    boost = pygame.Surface((WIDTH, HEIGHT))
    boost.fill((10, 6, 22))
    surf.blit(boost, (0, 0), special_flags=pygame.BLEND_ADD)

    # vignette - darken edges, focus on center
    vig = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    max_r = int(math.hypot(WIDTH, HEIGHT) * 0.55)
    for r in range(max_r, 0, -6):
        alpha = max(0, int(55 * (1 - r / max_r)))
        pygame.draw.circle(vig, (0, 0, 0, alpha), (WIDTH//2, HEIGHT//2), r)
    surf.blit(vig, (0, 0))

    return surf


def _build_star_layer(count, size, brightness):
    surf = pygame.Surface((WIDTH, HEIGHT*2))
    surf.fill((0, 0, 0))
    surf.set_colorkey((0, 0, 0))

    for _ in range(count):
        x  = random.randint(0, WIDTH-1)
        y  = random.randint(0, HEIGHT*2-1)
        b  = random.randint(max(0, brightness-50), min(255, brightness+20))
        pygame.draw.circle(surf, (b, b, min(255, b+25)), (x, y), size)

        if size >= 2 and random.random() < 0.45:
            halo = pygame.Surface((size*8, size*8), pygame.SRCALPHA)
            hb   = max(0, b-100)
            pygame.draw.circle(halo, (hb, hb, min(255,hb+40), 50),
                               (size*4, size*4), size*4)
            surf.blit(halo, (x-size*4, y-size*4))
    return surf


# ─── Main class ──────────────────────────────────────────────────────────────

class Background:
    def __init__(self):
        print("  Building nebula...", end=" ", flush=True)
        self.nebula = _build_nebula()
        print("OK")

        self.star_layers = [
            _build_star_layer(180, 1, 100),   # far - tiny & dim
            _build_star_layer(90,  2, 160),   # mid
            _build_star_layer(40,  3, 215),   # close - large & bright
        ]
        self.speeds  = [0.22, 0.55, 1.2]
        self.offsets = [0.0,  0.0,  0.0]

        # hero stars - a few big bright ones that pulse gently
        self.hero_stars = [
            {
                "x":  random.randint(60, WIDTH-60),
                "y":  random.randint(60, HEIGHT-60),
                "r":  random.randint(3, 6),
                "ph": random.uniform(0, math.pi*2),
                "color": random.choice([
                    (210, 230, 255),
                    (255, 245, 190),
                    (180, 255, 240),
                    (255, 190, 220),
                ]),
            }
            for _ in range(10)
        ]
        self._tick = 0

    def update(self):
        for i in range(3):
            self.offsets[i] = (self.offsets[i] + self.speeds[i]) % HEIGHT
        self._tick += 1

    def draw(self, surface):
        # 1. static nebula
        surface.blit(self.nebula, (0, 0))

        # 2. parallax star layers (additive blend = stars glow on dark bg)
        for i, layer in enumerate(self.star_layers):
            off = int(self.offsets[i])
            surface.blit(layer, (0, off - HEIGHT), special_flags=pygame.BLEND_ADD)
            surface.blit(layer, (0, off),           special_flags=pygame.BLEND_ADD)

        # 3. pulsing hero stars with soft halos
        for s in self.hero_stars:
            pulse  = 0.75 + 0.25 * math.sin(self._tick * 0.035 + s["ph"])
            r      = max(1, int(s["r"] * pulse))
            cx, cy = s["x"], s["y"]

            # outer glow ring
            glow_r = r * 6
            glow   = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
            gc     = tuple(min(255, int(c * 0.45)) for c in s["color"])
            pygame.draw.circle(glow, (*gc, 40), (glow_r, glow_r), glow_r)
            surface.blit(glow, (cx - glow_r, cy - glow_r))

            # bright core + white center point
            pygame.draw.circle(surface, s["color"], (cx, cy), r)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), max(1, r-1))
