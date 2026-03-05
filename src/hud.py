import pygame
import os
from src.settings import WIDTH, HEIGHT, WHITE, YELLOW, RED, CYAN, GREEN, ORANGE, GREY, ASSET_FONT

# loads and caches fonts so we don't reload each frame
_font_cache = {}

def get_font(size):
    if size in _font_cache:
        return _font_cache[size]
    path = os.path.join(ASSET_FONT, "orbitron.ttf")
    try:
        f = pygame.font.Font(path, size)
    except:
        f = pygame.font.SysFont("Arial", size, bold=True)
    _font_cache[size] = f
    return f


class HUD:
    """Draws the score, lives, and level indicator on screen."""
    def __init__(self):
        self.font_big   = get_font(26)
        self.font_med   = get_font(18)
        self.font_small = get_font(14)

        # level-up notification
        self.levelup_timer = 0
        self.levelup_text  = ""

    def show_levelup(self, level):
        self.levelup_timer = 160   # show for ~2.5 seconds
        self.levelup_text  = f"LEVEL {level}!"

    def update(self):
        if self.levelup_timer > 0:
            self.levelup_timer -= 1

    def draw(self, surface, score, lives, level):
        # ── top bar background ──────────────────────────────
        bar = pygame.Surface((WIDTH, 46), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 140))
        surface.blit(bar, (0, 0))

        # ── score (left) ────────────────────────────────────
        score_surf = self.font_big.render(f"SCORE  {score:05d}", True, CYAN)
        surface.blit(score_surf, (16, 10))

        # ── level (center) ──────────────────────────────────
        lvl_surf = self.font_big.render(f"LVL {level}", True, YELLOW)
        surface.blit(lvl_surf, (WIDTH // 2 - lvl_surf.get_width() // 2, 10))

        # ── lives as heart icons (right) ────────────────────
        self._draw_lives(surface, lives)

        # ── level-up notification ───────────────────────────
        if self.levelup_timer > 0:
            self._draw_levelup_banner(surface)

    def _draw_lives(self, surface, lives):
        heart_x = WIDTH - 16
        heart_y = 12

        for i in range(max(0, lives)):
            # small heart using two circles + triangle
            hx = heart_x - i * 32
            hy = heart_y
            pygame.draw.circle(surface, RED, (hx - 6, hy + 6), 9)
            pygame.draw.circle(surface, RED, (hx + 6, hy + 6), 9)
            pts = [(hx - 14, hy + 8), (hx + 14, hy + 8), (hx, hy + 24)]
            pygame.draw.polygon(surface, RED, pts)
            # bright top highlights
            pygame.draw.circle(surface, (255, 120, 120), (hx - 6, hy + 4), 4)
            pygame.draw.circle(surface, (255, 120, 120), (hx + 6, hy + 4), 4)

        # label
        label = self.font_small.render("LIVES", True, GREY)
        surface.blit(label, (WIDTH - 16 - max(0, lives - 1) * 32 - label.get_width() - 10, 30))

    def _draw_levelup_banner(self, surface):
        fade   = min(1.0, self.levelup_timer / 40)   # fade in/out
        alpha  = int(255 * fade)

        banner = pygame.Surface((320, 60), pygame.SRCALPHA)
        banner.fill((0, 0, 0, int(160 * fade)))
        bx = WIDTH // 2 - 160
        by = HEIGHT // 2 - 30
        surface.blit(banner, (bx, by))

        # main text with glow effect
        color  = (int(0 + 255 * fade), int(200 * fade), int(255 * fade))
        txt    = self.font_big.render(self.levelup_text, True, color)
        sub    = self.font_small.render("Speed increased!", True, (200, 200, 200))
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, by + 8))
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, by + 38))


def draw_score_popup(surface, x, y, value, font):
    """Little +1 / +3 popup that floats up when you collect an item."""
    color = (255, 220, 0) if value <= 1 else (0, 200, 255)
    sign  = "+" if value >= 0 else ""
    surf  = font.render(f"{sign}{value}", True, color)
    surface.blit(surf, (x - surf.get_width() // 2, y))
