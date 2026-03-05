import pygame
from src.settings   import WIDTH, HEIGHT, FPS, PLAYER_START_LIVES
from src.background import Background
from src.player     import Player
from src.items      import SpawnController
from src.bullet     import Bullet
from src.particles  import ParticleSystem
from src.hud        import HUD, get_font
from src.screens    import StartScreen, GameOverScreen
from src.audio      import AudioManager
from src.gfx        import ScreenShake, RingEffect, draw_glowing_sprite


# ─── Floating score popup ─────────────────────────────────────────────────────

class ScorePopup:
    def __init__(self):
        self.popups = []
        self.font   = get_font(18)

    def add(self, x, y, value):
        self.popups.append({"x": float(x), "y": float(y), "val": value, "t": 45})

    def update(self):
        for p in self.popups:
            p["y"] -= 1.1
            p["t"] -= 1
        self.popups = [p for p in self.popups if p["t"] > 0]

    def draw(self, surface):
        for p in self.popups:
            fade  = p["t"] / 45
            color = (255, 220, 0) if p["val"] <= 1 else (0, 210, 255)
            c     = tuple(int(ch * fade) for ch in color)
            sign  = "+" if p["val"] > 0 else ""
            surf  = self.font.render(f"{sign}{p['val']}", True, c)
            surface.blit(surf, (int(p["x"]) - surf.get_width() // 2, int(p["y"])))


# ─── Game class ───────────────────────────────────────────────────────────────

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()

        self.bg    = Background()
        self.audio = AudioManager()

        self.start_screen    = StartScreen(self.bg)
        self.gameover_screen = GameOverScreen(self.bg)

        # off-screen canvas so screen shake works cleanly
        self.canvas  = pygame.Surface((WIDTH, HEIGHT))
        self.state   = "start"
        self.running = True
        self._init_game()

    def _init_game(self):
        self.player    = Player()
        self.items     = pygame.sprite.Group()
        self.bullets   = pygame.sprite.Group()   # player's shots
        self.spawner   = SpawnController()
        self.particles = ParticleSystem()
        self.hud       = HUD()
        self.popups    = ScorePopup()
        self.shake     = ScreenShake()
        self.rings     = RingEffect()

        self.score        = 0
        self.lives        = PLAYER_START_LIVES
        self.level        = 1
        self.score_timer  = 0   # counts frames for time-based scoring

    # ─── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            if   self.state == "start":    self._run_start()
            elif self.state == "playing":  self._run_playing()
            elif self.state == "gameover": self._run_gameover()

    # ─── Start screen ─────────────────────────────────────────────────────────

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

    # ─── Playing ──────────────────────────────────────────────────────────────

    def _run_playing(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "start"
                if event.key == pygame.K_m:
                    self.audio.toggle_music()

        keys = pygame.key.get_pressed()

        # shoot on SPACE (held down = rapid fire limited by cooldown)
        if keys[pygame.K_SPACE]:
            shot = self.player.try_shoot()
            if shot:
                cx, y = shot
                self.bullets.add(Bullet(cx, y))
                self.audio.play("shoot")

        # updates
        self.bg.update()
        self.player.update(keys)
        self.bullets.update()
        self.hud.update()
        self.popups.update()
        self.particles.update()
        self.rings.update()
        self.shake.update()

        new_items = self.spawner.update()
        for item in new_items:
            self.items.add(item)
        self.items.update()

        self._check_collisions()

        # time-based scoring: +1 every second survived
        self.score_timer += 1
        if self.score_timer >= 60:
            self.score_timer = 0
            self.score += 1

        if self.lives < 0:
            self.gameover_screen.set_data(self.score, self.level)
            self.state = "gameover"
            return

        self._draw_game(self.canvas)

        ox, oy = self.shake.offset
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.canvas, (ox, oy))
        pygame.display.flip()

    # ─── Draw ─────────────────────────────────────────────────────────────────

    def _draw_game(self, surface):
        self.bg.draw(surface)

        for item in self.items:
            draw_glowing_sprite(surface, item.image,
                                item.rect.x, item.rect.y,
                                item.get_glow_color(), radius=14)

        # draw bullets with their built-in glow
        for b in self.bullets:
            b.draw_custom(surface)

        self.particles.draw(surface)
        self.rings.draw(surface)
        self.player.draw(surface)
        self.popups.draw(surface)
        self.hud.draw(surface, self.score, self.lives, self.level)

    # ─── Collisions ───────────────────────────────────────────────────────────

    def _check_collisions(self):
        from src.items import GoodItem, BadItem

        # 1. player vs items
        player_hit_box = self.player.rect.inflate(-18, -18)
        for item in list(self.items):
            if not player_hit_box.colliderect(item.rect):
                continue
            cx, cy = item.rect.center

            if isinstance(item, GoodItem):
                self._collect_good(item, cx, cy)
            elif isinstance(item, BadItem):
                self._player_hit_bad(item, cx, cy)

        # 2. bullets vs bad items
        for bullet in list(self.bullets):
            for item in list(self.items):
                if not isinstance(item, BadItem):
                    continue
                if bullet.rect.colliderect(item.rect):
                    cx, cy = item.rect.center
                    self._bullet_destroy(bullet, item, cx, cy)
                    break   # one bullet hits one target

    def _collect_good(self, item, cx, cy):
        self.score += item.score_val
        self.popups.add(cx, cy - 20, item.score_val)
        self.audio.play("collect")
        self.particles.spawn_collect(cx, cy, color=item.get_glow_color())
        self.rings.spawn(cx, cy, color=item.get_glow_color(), max_r=60)
        item.kill()

        leveled = self.spawner.on_good_collected()
        if leveled:
            self.level = self.spawner.level
            self.hud.show_levelup(self.level)
            self.audio.play("levelup")
            self.particles.spawn_level_up(WIDTH, HEIGHT)
            self.shake.trigger(intensity=5, duration_frames=20)

    def _player_hit_bad(self, item, cx, cy):
        if self.player.take_hit():
            self.lives -= 1
            self.audio.play("hit")
            self.particles.spawn_explosion(cx, cy)
            self.rings.spawn(cx, cy, color=(220, 60, 30), max_r=80)
            self.shake.trigger(intensity=11, duration_frames=15)
            item.kill()

    def _bullet_destroy(self, bullet, item, cx, cy):
        """Bullet hits a bad item — destroy both, small explosion. No score."""
        bullet.kill()
        item.kill()
        self.audio.play("explosion")
        self.particles.spawn_explosion(cx, cy, color=(255, 120, 20), count=14)
        self.rings.spawn(cx, cy, color=(255, 140, 0), max_r=50)
        self.shake.trigger(intensity=4, duration_frames=8)

    # ─── Game Over ────────────────────────────────────────────────────────────

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
