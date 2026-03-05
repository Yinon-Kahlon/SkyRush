"""
Generate an energetic 128 BPM electronic space-shooter track.
Kick on 1&3, snare on 2&4, hi-hat every 8th, bass + synth arp.
Pure Python, no extra libraries needed.
"""

import wave, struct, math, random, os

SR   = 44100
BPM  = 128
BARS = 16       # 16 bars loop ~= 30 seconds

beat  = 60.0 / BPM          # 0.469 sec / beat
bar   = beat * 4            # 1.875 sec / bar
total = bar * BARS
N     = int(SR * total)

buf   = [0.0] * N

# ─── low-level oscillator helpers ───────────────────────────────────────────

def add_sine(t0, freq, dur, amp, decay=12.0):
    start = int(t0 * SR)
    end   = min(N, start + int(dur * SR))
    for i in range(end - start):
        t   = i / SR
        env = math.exp(-t * decay)
        buf[start + i] += math.sin(2 * math.pi * freq * t) * env * amp

def add_saw(t0, freq, dur, amp, n_harm=8, decay=8.0):
    """Sawtooth via additive harmonics — fatter sound for bass/lead"""
    for h in range(1, n_harm + 1):
        a = amp / h
        add_sine(t0, freq * h, dur, a, decay)

def add_noise(t0, dur, amp, high_pass=False):
    start = int(t0 * SR)
    end   = min(N, start + int(dur * SR))
    prev  = 0.0
    for i in range(end - start):
        t   = i / SR
        env = math.exp(-t * 30) if dur < 0.05 else max(0, 1 - t / dur) ** 2
        r   = random.uniform(-1, 1)
        if high_pass:
            r    = r - 0.97 * prev
            prev = r
        buf[start + i] += r * env * amp

def add_square(t0, freq, dur, amp, decay=6.0):
    """Square wave = harmonics 1, 3, 5, 7 ..."""
    for h in range(1, 8, 2):
        add_sine(t0, freq * h, dur, amp / h, decay)

# ─── instrument patterns ────────────────────────────────────────────────────

# Kick: deep sine punch + click
def kick(t0):
    add_sine(t0, 80,  0.18, 1.0,  decay=14)
    add_sine(t0, 55,  0.35, 0.7,  decay=8)
    add_noise(t0, 0.015, 0.5)

# Snare: tone + noise burst
def snare(t0):
    add_sine(t0,  200, 0.08, 0.35, decay=25)
    add_noise(t0, 0.12, 0.55)

# Hi-hat: short high-pass noise
def hihat(t0, amp=0.22):
    add_noise(t0, 0.025, amp, high_pass=True)

def open_hihat(t0):
    add_noise(t0, 0.12, 0.18, high_pass=True)

# ─── chord / scale (minor pentatonic in C) ─────────────────────────────────
# C2 G2 Bb2 / C3 G3 Bb3
BASS_PATTERN = [
    65.41, 65.41, 97.99,  65.41,   # C2 C2 G2 C2
    87.31, 87.31, 116.54, 87.31,   # F2 F2 Bb2 F2
    73.42, 73.42, 110.00, 73.42,   # D2 D2 A2 D2
    87.31, 87.31, 97.99,  87.31,   # F2 F2 G2 F2
]
ARP_NOTES = [
    261.63, 329.63, 392.00, 523.25,
    466.16, 392.00, 329.63, 261.63,
    293.66, 349.23, 440.00, 587.33,
    466.16, 392.00, 349.23, 293.66,
]

# ─── build track bar by bar ─────────────────────────────────────────────────

for b in range(BARS):
    t_bar = b * bar

    # ── drums ──────────────────────────────────────────────────────────────
    kick(t_bar)
    kick(t_bar + beat * 2)

    snare(t_bar + beat)
    snare(t_bar + beat * 3)

    # hi-hats every 8th note
    for i in range(8):
        amp = 0.28 if (i % 2 == 0) else 0.17
        hihat(t_bar + i * beat * 0.5, amp)

    # open hi-hat on the & of beat 4
    open_hihat(t_bar + beat * 3.5)

    # extra kick (4-on-the-floor feel from bar 4+)
    if b >= 4:
        kick(t_bar + beat * 1)
        kick(t_bar + beat * 3)

    # ── bass ───────────────────────────────────────────────────────────────
    bass_note = BASS_PATTERN[b % len(BASS_PATTERN)]
    # root on beat 1 & 3, 5th on beat 2.5
    add_saw(t_bar,                bass_note,      beat * 0.85, 0.45, n_harm=6, decay=9)
    add_saw(t_bar + beat,         bass_note * 1.5, beat * 0.4,  0.30, n_harm=5, decay=10)
    add_saw(t_bar + beat * 2,     bass_note,      beat * 0.85, 0.45, n_harm=6, decay=9)
    add_saw(t_bar + beat * 2.75,  bass_note * 0.75, beat * 0.3, 0.20, n_harm=4, decay=12)

    # ── lead arp (starts from bar 2) ───────────────────────────────────────
    if b >= 2:
        for i, note in enumerate(ARP_NOTES):
            t_note = t_bar + i * beat * 0.5
            add_saw(t_note, note,     beat * 0.35, 0.20, n_harm=5, decay=10)
            add_saw(t_note, note * 2, beat * 0.25, 0.07, n_harm=3, decay=14)

    # ── pad chord (from bar 4, long sustained notes) ───────────────────────
    if b >= 4:
        chord = [bass_note * 2, bass_note * 2.5, bass_note * 3, bass_note * 4]
        for note in chord:
            add_sine(t_bar, note, bar * 0.95, 0.06, decay=0.6)

# ─── normalize + add small fade-in to avoid click ───────────────────────────
max_v = max(abs(x) for x in buf) or 1.0
for i in range(N):
    buf[i] /= max_v
    buf[i]  = max(-1.0, min(1.0, buf[i]))
    # fade in first 0.1 sec
    if i < SR // 10:
        buf[i] *= i / (SR // 10)

# ─── write WAV ───────────────────────────────────────────────────────────────
out_path = os.path.join(os.path.dirname(__file__), "assets", "sounds", "music.wav")
with wave.open(out_path, "w") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    frames = bytearray()
    for s in buf:
        v = max(-32767, min(32767, int(s * 32767)))
        frames += struct.pack("<h", v)
        frames += struct.pack("<h", v)
    wf.writeframes(bytes(frames))

mb = os.path.getsize(out_path) / 1024 / 1024
print(f"Music generated: {out_path}  ({mb:.1f} MB, {total:.1f}s loop)")
