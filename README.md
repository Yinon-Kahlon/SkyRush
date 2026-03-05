# SkyRush

A fast-paced 2D space survival game built with Python and Pygame.

Pilot your ship through a cosmic storm — collect energy pickups, shoot down incoming
threats, and survive as long as you can. The game speeds up over time and launches
rush waves of enemies at higher levels.

---

## Installation

Requires **Python 3.9+**

```bash
git clone https://github.com/Yinon-Kahlon/SkyRush.git
cd SkyRush
pip install -r requirements.txt
python main.py
```

All assets are included in the repository — no additional downloads needed.

---

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move the ship |
| SPACE (hold) | Fire laser |
| M | Toggle background music |
| ESC | Return to main menu |
| Enter | Confirm on menus |

---

## Gameplay

- **Collect** stars and energy bolts rising from the bottom of the screen - **+100 points each**
- **Avoid** meteors and enemy ships - each hit costs 1 life
- **Shoot** obstacles with your laser to destroy them (defensive — no score bonus)
- You start with **3 lives** - the game ends when they run out

### Difficulty Scaling

The game scales on two independent axes:

1. **Level-ups** - every 8 good items collected, the level advances:
   - Item speed increases
   - Bad items spawn more frequently
   - Good items spawn less frequently
   - Rush waves grow in size

2. **Time pressure** - every 8 seconds, speed and spawn rate increase slightly
   regardless of score, so you can't just hide and wait

At **level 3+**, rush waves appear: bursts of fast meteors arriving in quick succession
that you need to dodge or shoot down.

---

## Features

- Procedural space background - nebula with 7 color regions built using additive blending,
  3-layer parallax star field, pulsing hero stars with soft halos
- Player ship with smooth tilt animation, multi-nozzle engine flame effect, and engine trail
- Shooting mechanic - hold SPACE for rapid fire, glowing cyan laser bolts
- Screen shake on hit, expanding ring pulses, and particle burst effects
- FM-synthesized background music at 130 BPM (pure Python `wave` / `math` stdlib — no external tools)
- Procedural laser and explosion sound effects, also generated with Python stdlib
- Floating +100 score popup on every item collection
- Start screen and animated game-over screen

---

## Project Structure

```
SkyRush/
├── main.py              # Entry point — initialises pygame and launches the game
├── generate_music.py    # One-time script that generates assets/sounds/music.wav
├── gen_shoot_sfx.py     # One-time script that generates assets/sounds/shoot.wav
├── requirements.txt
│
├── src/
│   ├── settings.py      # All constants (screen size, speeds, colors, asset paths)
│   ├── game.py          # Core Game class — state machine, collision handling, main loop
│   ├── player.py        # Player sprite — movement, tilt, shooting, invincibility frames
│   ├── items.py         # GoodItem, BadItem, RushItem, SpawnController (difficulty logic)
│   ├── bullet.py        # Laser bolt sprite — procedurally drawn with glow effect
│   ├── background.py    # Procedural nebula + parallax scrolling star layers
│   ├── particles.py     # Particle system (explosions, sparkle effects, level-up burst)
│   ├── gfx.py           # Visual helpers — glow surfaces, screen shake, ring pulse effects
│   ├── hud.py           # HUD rendering — score, lives, level, floating score popups
│   ├── screens.py       # StartScreen and GameOverScreen with animated elements
│   └── audio.py         # AudioManager — loads SFX and streams background music
│
└── assets/
    ├── images/
    │   ├── player/      # Ship sprite (Kenney Space Shooter Redux)
    │   └── items/       # Good and bad item sprites (Kenney Space Shooter Redux)
    ├── sounds/          # WAV audio files (music + SFX)
    └── fonts/           # Orbitron TTF font (Google Fonts)
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pygame` | 2.5.2 | Game engine — rendering, input, audio |

```bash
pip install -r requirements.txt
```

---

## Credits

| Asset | Source | License |
|-------|--------|---------|
| Ship & item sprites | [Kenney.nl - Space Shooter Redux](https://kenney.nl/assets/space-shooter-redux) | CC0 (Public Domain) |
| Orbitron font | [Google Fonts](https://fonts.google.com/specimen/Orbitron) | SIL OFL |
| Background music | Original FM synthesis - generated with Python stdlib | — |
| Sound effects | Procedurally generated with Python `wave` module | — |

---

*Final project — Python Programming course*
