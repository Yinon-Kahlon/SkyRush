# 🚀 SkyRush

> A fast-paced space survival game built with Python & Pygame.
> Pilot your ship through a cosmic storm — collect energy pickups, dodge meteors and enemy fighters, and survive as long as you can!

---

## 📸 Preview

```
  ★ Stars   +1 pt  |  ⚡ Bolts   +3 pts
  ☄ Meteors  -1 life  |  👾 Enemy Ships  -1 life
```

---

## 🛠 Installation

**Requirements:** Python 3.9+ and pip

```bash
# 1. Clone the repo
git clone https://github.com/Yinon-Kahlon/SkyRush.git
cd SkyRush

# 2. Install dependencies
pip install -r requirements.txt

# 3. (First run only) Download game assets
python download_assets.py

# 4. Launch the game
python main.py
```

---

## 🎮 How to Play

| Key | Action |
|-----|--------|
| **Arrow Keys** / **WASD** | Move the spaceship |
| **M** | Toggle background music on/off |
| **ESC** | Return to main menu |
| **Enter / Space** | Confirm on menus |

### Objective
- Collect **stars** (+1) and **energy bolts** (+3) that rise from the bottom of the screen
- Avoid **meteors** and **enemy ships** — each hit costs 1 life
- You start with **3 lives** — game over when you run out

### Difficulty Scaling
Every **10 good items** collected advances you to the next level:
- Item speed increases
- Obstacles spawn more frequently
- Good items spawn less frequently

---

## 📁 Project Structure

```
SkyRush/
├── main.py              # Entry point — initialises pygame and starts Game
├── download_assets.py   # One-time script to fetch sprites, sounds & fonts
├── requirements.txt     # Python dependencies
├── README.md            # This file
│
├── src/
│   ├── settings.py      # All constants (screen size, speeds, colors…)
│   ├── game.py          # Core Game class — state machine & main loop
│   ├── player.py        # Player sprite with tilt animation & i-frames
│   ├── items.py         # GoodItem, BadItem, SpawnController (level logic)
│   ├── background.py    # Parallax 3-layer star field
│   ├── particles.py     # Particle system (explosions, collect sparkles)
│   ├── hud.py           # Score / lives / level HUD + floating score popups
│   ├── screens.py       # StartScreen and GameOverScreen
│   └── audio.py         # Sound effects & background music manager
│
└── assets/
    ├── images/
    │   ├── player/      # Ship sprite
    │   ├── items/       # Good & bad item sprites
    │   ├── backgrounds/ # Space background (if downloaded)
    │   └── ui/          # UI elements
    ├── sounds/          # WAV/MP3 audio files
    └── fonts/           # Orbitron TTF font
```

---

## 📦 Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| `pygame` | 2.5.2 | Game engine — rendering, input, audio |

Install with:
```bash
pip install -r requirements.txt
```

---

## 🔮 TODO / Future Ideas

- [ ] High-score leaderboard saved to file
- [ ] Shield power-up item
- [ ] Boss enemy every 5 levels
- [ ] More ship skins to unlock
- [ ] Mobile touch controls

---

## 📜 Credits

| Asset | Source | License |
|-------|--------|---------|
| Spaceship & item sprites | [Kenney.nl – Space Shooter Redux](https://kenney.nl/assets/space-shooter-redux) | CC0 |
| Background music | [Kevin MacLeod – incompetech.com](https://incompetech.com) | CC BY 4.0 |
| Font (Orbitron) | [Google Fonts](https://fonts.google.com/specimen/Orbitron) | OFL |
| Sound effects | Procedurally generated with Python `wave` module | — |

---

*Final project for Introduction to Computer Engineering — Python course*
