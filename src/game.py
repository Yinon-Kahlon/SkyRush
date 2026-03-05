import pygame
import sys
from src.settings   import WIDTH, HEIGHT, FPS, PLAYER_START_LIVES
from src.background import Background
from src.player     import Player
from src.items      import SpawnController
from src.particles  import ParticleSystem
from src.hud        import HUD, get_font, draw_score_popup
from src.screens    import StartScreen, GameOverScreen
from src.audio      import AudioManager

# score popup helper - stores a list of (x, y, value, timer) tuples
class ScorePopup:
    def __init__(self):
        self.popups = []   # (x, y, value, timer, dy)
        self.font   = get_font(16)

    def add(self, x, y, value):
        self.popups.append({"x": x, "y": float(y), "val": value, "t": 40})

    def update(self):
        for p in self.popups:
            p["y"] -= 0.8
            p["t"] -= 1
        self.popups = [p for p in self.popups if p["t"] > 0]

    def draw(self, surface):
        for p in self.popups:
            alpha  = min(255, p["t"] * 8)
            color  = (255, 220, 0) if p["val"] <= 1 else (0, 210, 255)
            sign   = "+" if p["val"] > 0 else ""
            surf   = self.font.render(f"{sign}{p['val']}", True, color)
            surface.blit(surf, (int(p["x"]) - surf.get_width() // 2, int(p["y"])))


class Game:
    def __init__(self, screen):
        self.screen    = screen
        self.clock     = pygame.time.Clock()
        self.bg        = Background()
        self.audio     = AudioManager()

        self.start_screen     = StartScreen(self.bg)
        self.gameover_screen  = GameOverScreen(self.bg)

        # game state: "start", "playing", "gameover"
        self.state = "start"

        self._init_game()

    def _init_game(self):
        """Reset everything to start a fresh game."""
        self.player    = Player()
        self.items     = pygame.sprite.Group()
        self.spawner   = SpawnController()
        self.particles = ParticleSystem()
        self.hud       = HUD()
        self.popups    = ScorePopup()

        self.score  = 0
        self.lives  = PLAYER_START_LIVES
        self.level  = 1
        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)

            if self.state == "start":
                self._run_start()
            elif self.state == "playing":
                self._run_playing()
            elif self.state == "gameover":
                self._run_gameover()

    # ─── Start screen loop ────────────────────────────────────────────────────

    def _run_start(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            action = self.start_screen.handle_event(event)
            if action == "start":
                self._init_game()
                self.state = "playing"
            elif action == "quit":
                self.running = False

        self.start_screen.update()
        self.start_screen.draw(self.screen)
        pygame.display.flip()

    # ─── Main gameplay loop ───────────────────────────────────────────────────

    def _run_playing(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "start"
                if event.key == pygame.K_m:
                    is_on = self.audio.toggle_music()
                    # small feedback - could add a visual later

        keys = pygame.key.get_pressed()

        # updates
        self.player.update(keys)
        self.bg.update()
        self.hud.update()
        self.popups.update()

        # spawn new items
        new_items = self.spawner.update()
        for item in new_items:
            self.items.add(item)
        self.items.update()
        self.particles.update()

        # collision detection
        self._check_collisions()

        # check game over
        if self.lives < 0:
            self.gameover_screen.set_data(self.score, self.level)
            self.state = "gameover"
            return

        # draw everything
        self.bg.draw(self.screen)
        self.items.draw(self.screen)
        self.particles.draw(self.screen)
        self.player.draw(self.screen)
        self.popups.draw(self.screen)
        self.hud.draw(self.screen, self.score, self.lives, self.level)

        pygame.display.flip()

    def _check_collisions(self):
        from src.items import GoodItem, BadItem

        # use slightly smaller rect for fairer collision (feels better to play)
        player_rect = self.player.rect.inflate(-16, -16)

        for item in list(self.items):
            if not player_rect.colliderect(item.rect):
                continue

            cx, cy = item.rect.center

            if isinstance(item, GoodItem):
                self.score += item.score_val
                self.popups.add(cx, cy, item.score_val)
                self.audio.play("collect")
                self.particles.spawn_collect(cx, cy, color=item.get_glow_color())
                item.kill()

                # check for level up
                leveled = self.spawner.on_good_collected()
                if leveled:
                    self.level = self.spawner.level
                    self.hud.show_levelup(self.level)
                    self.audio.play("levelup")
                    self.particles.spawn_level_up(WIDTH, HEIGHT)

            elif isinstance(item, BadItem):
                hit = self.player.take_hit()
                if hit:
                    self.lives -= 1
                    self.audio.play("hit")
                    self.particles.spawn_explosion(cx, cy)
                    item.kill()

    # ─── Game Over screen loop ────────────────────────────────────────────────

    def _run_gameover(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            action = self.gameover_screen.handle_event(event)
            if action == "retry":
                self._init_game()
                self.state = "playing"
            elif action == "quit":
                self.running = False

        self.gameover_screen.update()
        self.gameover_screen.draw(self.screen)
        pygame.display.flip()
