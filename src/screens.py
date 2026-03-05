import pygame
import math
import random
from src.settings  import WIDTH, HEIGHT, WHITE, CYAN, YELLOW, RED, DARK_BLUE, GREY, ORANGE
from src.hud       import get_font

# ─── shared helper ───────────────────────────────────────────────────────────

def draw_text_centered(surface, text, font, color, y, shadow=True):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surface.blit(s, (WIDTH // 2 - s.get_width() // 2 + 2, y + 2))
    surf = font.render(text, True, color)
    surface.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

def draw_button(surface, text, font, rect, hovered=False):
    color  = (0, 160, 220) if hovered else (0, 100, 160)
    border = (0, 220, 255) if hovered else (0, 150, 200)
    pygame.draw.rect(surface, color,  rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    surf = font.render(text, True, WHITE)
    surface.blit(surf, (rect.centerx - surf.get_width() // 2,
                        rect.centery - surf.get_height() // 2))


# ─── Start Screen ─────────────────────────────────────────────────────────────

class StartScreen:
    def __init__(self, bg):
        self.bg          = bg
        self.font_title  = get_font(62)
        self.font_sub    = get_font(20)
        self.font_small  = get_font(14)
        self.font_btn    = get_font(22)
        self.timer       = 0

        self.btn_start = pygame.Rect(WIDTH // 2 - 110, 360, 220, 52)
        self.btn_quit  = pygame.Rect(WIDTH // 2 - 110, 428, 220, 52)

        # floating star decorations
        self.deco_stars = [
            {"x": random.randint(0, WIDTH), "y": random.randint(60, HEIGHT - 60),
             "r": random.randint(2, 5), "speed": random.uniform(0.3, 1.0),
             "color": random.choice([CYAN, YELLOW, (255, 100, 100)])}
            for _ in range(12)
        ]

    def update(self):
        self.timer += 1
        self.bg.update()
        for s in self.deco_stars:
            s["y"] -= s["speed"]
            if s["y"] < 0:
                s["y"]  = HEIGHT
                s["x"]  = random.randint(0, WIDTH)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_start.collidepoint(event.pos):
                return "start"
            if self.btn_quit.collidepoint(event.pos):
                return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "start"
            if event.key == pygame.K_ESCAPE:
                return "quit"
        return None

    def draw(self, surface):
        self.bg.draw(surface)

        # floating decoration stars
        for s in self.deco_stars:
            pygame.draw.circle(surface, s["color"], (int(s["x"]), int(s["y"])), s["r"])

        # title with pulsing glow
        pulse = 0.5 + 0.5 * math.sin(self.timer * 0.04)
        r = int(50  + 50  * pulse)
        g = int(180 + 75  * pulse)
        b = int(255)
        title_color = (r, g, b)
        draw_text_centered(surface, "SKY RUSH", self.font_title, title_color, 120)

        # subtitle
        draw_text_centered(surface, "Survive the cosmic storm", self.font_sub, GREY, 210)

        # instructions
        lines = [
            "Arrow Keys / WASD  -  Move",
            "SPACE  -  Shoot (destroy bad items!)",
            "Collect STARS (+1) and BOLTS (+3)",
            "Avoid METEORS and ENEMY SHIPS",
            "M  -  Toggle Music",
        ]
        for i, line in enumerate(lines):
            draw_text_centered(surface, line, self.font_small, (170, 190, 210), 265 + i * 22)

        # buttons
        mx, my = pygame.mouse.get_pos()
        draw_button(surface, "PLAY",  self.font_btn, self.btn_start,
                    hovered=self.btn_start.collidepoint(mx, my))
        draw_button(surface, "QUIT",  self.font_btn, self.btn_quit,
                    hovered=self.btn_quit.collidepoint(mx, my))

        # version / credits
        credit = self.font_small.render("Assets: Kenney.nl (CC0)  |  Music: original FM synthesis", True, (80, 80, 100))
        surface.blit(credit, (WIDTH // 2 - credit.get_width() // 2, HEIGHT - 22))


# ─── Game Over Screen ─────────────────────────────────────────────────────────

class GameOverScreen:
    def __init__(self, bg):
        self.bg         = bg
        self.font_big   = get_font(52)
        self.font_med   = get_font(24)
        self.font_small = get_font(16)
        self.font_btn   = get_font(22)
        self.timer      = 0

        self.btn_retry = pygame.Rect(WIDTH // 2 - 120, 400, 240, 52)
        self.btn_quit  = pygame.Rect(WIDTH // 2 - 120, 468, 240, 52)

        # data set from outside
        self.final_score = 0
        self.final_level = 1

    def set_data(self, score, level):
        self.final_score = score
        self.final_level = level
        self.timer       = 0

    def update(self):
        self.timer += 1
        self.bg.update()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_retry.collidepoint(event.pos):
                return "retry"
            if self.btn_quit.collidepoint(event.pos):
                return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "retry"
            if event.key == pygame.K_ESCAPE:
                return "quit"
        return None

    def draw(self, surface):
        self.bg.draw(surface)

        # dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # "GAME OVER" flashing red
        flash = abs(math.sin(self.timer * 0.05))
        color = (int(200 + 55 * flash), int(30 * flash), int(30 * flash))
        draw_text_centered(surface, "GAME OVER", self.font_big, color, 110)

        # score and level
        draw_text_centered(surface, f"Final Score:  {self.final_score:05d}",
                           self.font_med, CYAN, 215)
        draw_text_centered(surface, f"Reached Level {self.final_level}",
                           self.font_med, YELLOW, 255)

        # motivational line
        if self.final_score >= 50:
            msg = "Incredible piloting!"
        elif self.final_score >= 20:
            msg = "Not bad, space cadet."
        else:
            msg = "The asteroid belt is brutal..."
        draw_text_centered(surface, msg, self.font_small, GREY, 305)

        # buttons
        mx, my = pygame.mouse.get_pos()
        draw_button(surface, "PLAY AGAIN", self.font_btn, self.btn_retry,
                    hovered=self.btn_retry.collidepoint(mx, my))
        draw_button(surface, "QUIT",       self.font_btn, self.btn_quit,
                    hovered=self.btn_quit.collidepoint(mx, my))
