"""
Small collection of visual helpers used across the game.
Glow, screen-shake, tint, etc.
"""
import pygame
import math
import random


def make_glow_surf(width, height, color, radius=18):
    """
    Returns a Surface with a soft colored halo.
    Blit it behind a sprite to get a glow effect.
    """
    w = width  + radius * 2
    h = height + radius * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    steps = max(1, radius // 3)
    for r in range(radius, 0, -steps):
        alpha = int(90 * (r / radius) ** 0.6)
        cr    = tuple(min(255, int(c + (255 - c) * 0.1)) for c in color)
        pygame.draw.ellipse(
            surf, (*cr, alpha),
            (cx - width//2 - r//2, cy - height//2 - r//2,
             width + r, height + r)
        )
    return surf


def draw_glowing_sprite(surface, sprite_surf, x, y, glow_color, radius=16):
    """Draw sprite_surf at (x,y) with a colored glow halo behind it."""
    glow = make_glow_surf(sprite_surf.get_width(), sprite_surf.get_height(),
                          glow_color, radius)
    surface.blit(glow, (x - radius, y - radius))
    surface.blit(sprite_surf, (x, y))


def draw_ring_pulse(surface, cx, cy, radius, color, alpha):
    """Expanding ring - used for collect/hit feedback."""
    if alpha <= 0:
        return
    ring = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
    pygame.draw.circle(ring, (*color, min(255, alpha)), (radius+2, radius+2), radius, 3)
    surface.blit(ring, (cx - radius - 2, cy - radius - 2))


# ─── Screen Shake ────────────────────────────────────────────────────────────

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.ox = 0   # current offset x
        self.oy = 0   # current offset y

    def trigger(self, intensity=8, duration_frames=12):
        # just store max intensity, decays each frame
        self.intensity = max(self.intensity, intensity)
        self._decay = intensity / max(1, duration_frames)

    def update(self):
        if self.intensity > 0:
            self.ox = random.uniform(-self.intensity, self.intensity)
            self.oy = random.uniform(-self.intensity * 0.6, self.intensity * 0.6)
            self.intensity = max(0.0, self.intensity - self._decay)
        else:
            self.ox = 0
            self.oy = 0

    @property
    def offset(self):
        return (int(self.ox), int(self.oy))


# ─── Ring Pulse Manager ──────────────────────────────────────────────────────

class RingEffect:
    """Expanding ring on collect / hit."""
    def __init__(self):
        self.rings = []  # list of {cx, cy, r, max_r, color, life}

    def spawn(self, cx, cy, color=(255, 220, 0), max_r=55):
        self.rings.append({"cx": cx, "cy": cy, "r": 0,
                           "max_r": max_r, "color": color, "life": 1.0})

    def update(self):
        for ring in self.rings:
            ring["r"]    += 3.5
            ring["life"] -= 0.06
        self.rings = [r for r in self.rings if r["life"] > 0 and r["r"] < r["max_r"]]

    def draw(self, surface):
        for ring in self.rings:
            alpha = int(255 * ring["life"])
            draw_ring_pulse(surface, ring["cx"], ring["cy"],
                            int(ring["r"]), ring["color"], alpha)
