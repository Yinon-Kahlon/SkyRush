import pygame
import random
import math

# simple particle system - used for explosions and collect effects

class Particle:
    def __init__(self, x, y, color, speed, angle, life, size=4):
        self.x     = float(x)
        self.y     = float(y)
        self.color = color
        self.life  = life
        self.max_life = life
        self.size  = size
        self.vx    = math.cos(math.radians(angle)) * speed
        self.vy    = math.sin(math.radians(angle)) * speed
        self.gravity = 0.05

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += self.gravity
        self.vx  *= 0.97   # slight air resistance
        self.life -= 1

    def is_dead(self):
        return self.life <= 0

    def draw(self, surface):
        alpha  = int(255 * (self.life / self.max_life))
        fade   = self.life / self.max_life
        cur_sz = max(1, int(self.size * fade))
        r, g, b = self.color
        # fade toward black
        rc = int(r * fade)
        gc = int(g * fade)
        bc = int(b * fade)
        pygame.draw.circle(surface, (rc, gc, bc), (int(self.x), int(self.y)), cur_sz)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn_explosion(self, x, y, color=(220, 80, 30), count=22):
        """Big burst for taking damage or destroying enemy."""
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 6)
            life  = random.randint(20, 45)
            size  = random.randint(3, 7)
            # mix in some yellow/white sparks
            if random.random() < 0.3:
                c = (255, random.randint(200, 255), 0)
            else:
                c = color
            self.particles.append(Particle(x, y, c, speed, angle, life, size))

    def spawn_collect(self, x, y, color=(255, 220, 0), count=14):
        """Smaller sparkle effect for picking up a good item."""
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(1, 4)
            life  = random.randint(15, 30)
            size  = random.randint(2, 5)
            self.particles.append(Particle(x, y, color, speed, angle, life, size))

    def spawn_level_up(self, screen_w, screen_h, count=60):
        """Burst across the whole screen for level up."""
        for _ in range(count):
            x     = random.randint(0, screen_w)
            y     = random.randint(0, screen_h)
            angle = random.uniform(0, 360)
            speed = random.uniform(1, 3)
            life  = random.randint(25, 55)
            color = random.choice([(0, 200, 255), (150, 50, 255), (255, 220, 0)])
            self.particles.append(Particle(x, y, color, speed, angle, life, 4))

    def update(self):
        for p in self.particles:
            p.update()
        # remove dead ones
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
