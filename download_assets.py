"""
Download all SkyRush game assets from free/CC0 sources.
Run once before first launch.
"""

import urllib.request
import os
import zipfile
import shutil
import math
import wave
import struct

BASE   = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(BASE, "assets", "images")
SOUNDS = os.path.join(BASE, "assets", "sounds")
FONTS  = os.path.join(BASE, "assets", "fonts")

def dl(url, dest, label=""):
    tag = label or os.path.basename(dest)
    print(f"  Downloading {tag} ...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=40) as r, open(dest, "wb") as f:
            f.write(r.read())
        size = os.path.getsize(dest)
        print(f"OK  ({size//1024} KB)")
        return True
    except Exception as e:
        print(f"FAIL  ({e})")
        return False

# ─────────────────────────────────────────────
# 1. Kenney Space Shooter Redux  (CC0)
# ─────────────────────────────────────────────
def get_kenney_sprites():
    url = ("https://kenney.nl/media/pages/assets/space-shooter-redux/"
           "b31285e83d-1677669442/kenney_space-shooter-redux.zip")
    zp  = os.path.join(BASE, "_kenney.zip")
    if not dl(url, zp, "kenney_space-shooter-redux.zip"):
        return False

    tmp = os.path.join(BASE, "_tmp_k")
    os.makedirs(tmp, exist_ok=True)
    with zipfile.ZipFile(zp, "r") as z:
        z.extractall(tmp)

    # index every PNG
    idx = {}
    for r, _, files in os.walk(tmp):
        for f in files:
            if f.lower().endswith(".png"):
                idx[f] = os.path.join(r, f)

    copies = [
        # (candidates, dest)
        (["playerShip1_blue.png","playerShip2_blue.png","player.png"],
         os.path.join(IMAGES, "player", "ship.png")),
        (["powerupBlue_star.png","powerupYellow_star.png","powerupBlue.png"],
         os.path.join(IMAGES, "items", "good_item.png")),
        (["powerupBlue_bolt.png","powerupYellow_bolt.png","powerupBlue_shield.png"],
         os.path.join(IMAGES, "items", "good_item2.png")),
        (["meteorBrown_big1.png","meteorGrey_big1.png","meteor_big.png"],
         os.path.join(IMAGES, "items", "bad_item.png")),
        (["enemyBlack1.png","enemyRed1.png","enemyBlue1.png"],
         os.path.join(IMAGES, "items", "bad_item2.png")),
        (["laserBlue01.png","laserBlue06.png","laserRed01.png"],
         os.path.join(IMAGES, "player", "laser.png")),
        (["explosion5.png","explosion4.png"],
         os.path.join(IMAGES, "ui", "explosion.png")),
    ]
    for candidates, dest in copies:
        for c in candidates:
            if c in idx:
                shutil.copy(idx[c], dest)
                print(f"    sprite: {c} -> {os.path.relpath(dest, BASE)}")
                break

    shutil.rmtree(tmp)
    os.remove(zp)
    return True

# ─────────────────────────────────────────────
# 2. Space background  (NASA public domain)
# ─────────────────────────────────────────────
def get_background():
    dest = os.path.join(IMAGES, "backgrounds", "space_bg.jpg")
    urls = [
        # Pillars of Creation (Webb) - NASA public domain
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Webb%27s_view_of_the_Pillars_of_Creation_%28NIRCam_image%29.png/800px-Webb%27s_view_of_the_Pillars_of_Creation_%28NIRCam_image%29.png",
        # Cat's Eye Nebula - public domain
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Catseye-big.jpg/800px-Catseye-big.jpg",
        # Generic starfield from Wikimedia
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Earth_from_Space.jpg/800px-Earth_from_Space.jpg",
    ]
    for url in urls:
        if dl(url, dest, "space_bg.jpg"):
            return True
    return False

# ─────────────────────────────────────────────
# 3. Orbitron font  (OFL / open)
# ─────────────────────────────────────────────
def get_font():
    dest = os.path.join(FONTS, "orbitron.ttf")
    url  = ("https://raw.githubusercontent.com/google/fonts/main/"
            "ofl/orbitron/Orbitron%5Bwght%5D.ttf")
    return dl(url, dest, "Orbitron.ttf")

# ─────────────────────────────────────────────
# 4. Background music  (CC-BY Kevin MacLeod)
# ─────────────────────────────────────────────
def get_music():
    dest = os.path.join(SOUNDS, "music.ogg")
    urls = [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cipher.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Teller%20of%20the%20Tales.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Digital%20Lemonade.mp3",
    ]
    for url in urls:
        if dl(url, dest.replace(".ogg", ".mp3"), "music.mp3"):
            # rename to .mp3 since that's what we got
            mp3 = dest.replace(".ogg", ".mp3")
            if os.path.exists(mp3):
                os.rename(mp3, mp3)   # keep as .mp3
                # update reference path
                open(os.path.join(SOUNDS, "music_source.txt"), "w").write(mp3)
            return True
    return False

# ─────────────────────────────────────────────
# 5. Generate SFX with pure Python (no deps)
# ─────────────────────────────────────────────
def make_wav(path, freq, duration, style="sine", volume=0.7):
    """Write a raw WAV file — no numpy needed."""
    sr      = 44100
    n       = int(sr * duration)
    frames  = []
    for i in range(n):
        t     = i / sr
        decay = max(0.0, 1.0 - t / duration)
        if style == "sine":
            raw = math.sin(2 * math.pi * freq * t)
        elif style == "square":
            raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif style == "chirp":
            f_t  = freq * (1 + 2 * t / duration)
            raw  = math.sin(2 * math.pi * f_t * t)
        elif style == "noise":
            import random
            raw = random.uniform(-1, 1) * decay
        else:
            raw = math.sin(2 * math.pi * freq * t)
        val = int(raw * decay * volume * 32767)
        val = max(-32768, min(32767, val))
        s   = struct.pack("<h", val)
        frames.append(s + s)          # stereo

    with wave.open(path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b"".join(frames))
    print(f"  Generated SFX: {os.path.basename(path)}")

def generate_sfx():
    sfx = [
        ("collect.wav",  880,  0.18, "chirp",  0.6),
        ("hit.wav",      160,  0.35, "square", 0.8),
        ("explosion.wav",80,   0.55, "noise",  0.9),
        ("levelup.wav",  660,  0.70, "chirp",  0.55),
    ]
    for fname, freq, dur, style, vol in sfx:
        path = os.path.join(SOUNDS, fname)
        if not os.path.exists(path) or os.path.getsize(path) < 1000:
            make_wav(path, freq, dur, style, vol)

# ─────────────────────────────────────────────
# 6. Generate looping music WAV  (procedural)
# ─────────────────────────────────────────────
def generate_music():
    path = os.path.join(SOUNDS, "music.wav")
    if os.path.exists(path) and os.path.getsize(path) > 50000:
        print("  Music already exists, skipping")
        return

    print("  Generating procedural space music ...", end=" ", flush=True)
    sr       = 44100
    duration = 30       # 30-second loop
    n        = sr * duration
    frames   = []

    # simple arpeggiated melody over a pad
    base_notes = [261.63, 311.13, 392.00, 466.16,   # C4 Eb4 G4 Bb4 (Cm7)
                  349.23, 415.30, 523.25, 622.25]    # F4 Ab4 C5 Eb5

    def osc(freq, t, wave="sine"):
        if wave == "sine":
            return math.sin(2 * math.pi * freq * t)
        elif wave == "tri":
            p = (t * freq) % 1.0
            return 4 * abs(p - 0.5) - 1
        return 0.0

    for i in range(n):
        t        = i / sr
        beat     = t * 2           # 120 bpm
        note_idx = int(beat) % len(base_notes)
        note2    = int(beat * 2) % len(base_notes)
        freq1    = base_notes[note_idx]
        freq2    = base_notes[note2] * 2

        pad      = osc(freq1,       t, "tri")  * 0.18
        arp      = osc(freq2,       t, "sine") * 0.12 * (0.5 + 0.5 * math.sin(beat * math.pi * 4))
        bass     = osc(freq1 / 2,   t, "sine") * 0.20
        ambience = osc(freq1 * 1.5, t, "sine") * 0.07

        sample = pad + arp + bass + ambience
        val    = max(-32767, min(32767, int(sample * 32767)))
        s      = struct.pack("<h", val)
        frames.append(s + s)

    with wave.open(path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b"".join(frames))
    print(f"OK  ({os.path.getsize(path)//1024} KB)")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  SkyRush - Asset Downloader")
    print("=" * 50)

    print("\n[1/5] Kenney sprites (CC0)...")
    if not get_kenney_sprites():
        print("  Kenney download failed — game uses procedural sprites as fallback")

    print("\n[2/5] Space background (public domain)...")
    if not get_background():
        print("  Background download failed — game generates star field instead")

    print("\n[3/5] Orbitron font (OFL)...")
    if not get_font():
        print("  Font download failed — game will use system font")

    print("\n[4/5] Background music...")
    music_mp3 = os.path.join(SOUNDS, "music.mp3")
    music_ogg = os.path.join(SOUNDS, "music.ogg")
    has_music  = (os.path.exists(music_mp3) and os.path.getsize(music_mp3) > 10000) or \
                 (os.path.exists(music_ogg)  and os.path.getsize(music_ogg)  > 10000)
    if not has_music:
        if not get_music():
            print("  Music download failed — generating procedural music...")
            generate_music()

    print("\n[5/5] Sound effects...")
    generate_sfx()

    print("\n" + "=" * 50)
    print("  Done!  Files in assets/:")
    print("=" * 50)
    for root, _, files in os.walk(os.path.join(BASE, "assets")):
        for f in sorted(files):
            p    = os.path.join(root, f)
            rel  = os.path.relpath(p, BASE)
            size = os.path.getsize(p)
            flag = "[OK]" if size > 500 else "[EMPTY]"
            print(f"  {flag}  {rel}  ({size:,} bytes)")

if __name__ == "__main__":
    main()
