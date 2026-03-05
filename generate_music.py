"""
SkyRush — Space Soundtrack  (130 BPM, A natural minor)
FM synthesis + reverb simulation + dynamic arrangement.
Pure Python stdlib, no extra dependencies.

Structure:
  Bars  1-4  : Intro — kick + FM bass only
  Bars  5-8  : Build — add hi-hats + pad
  Bars  9-12 : Main  — full: arp + bass + drums
  Bars 13-16 : Drop  — add lead melody, max intensity
"""

import wave, struct, math, random, os

SR    = 44100
BPM   = 130
BARS  = 16

beat  = 60.0 / BPM      # 0.4615 s
bar   = beat * 4        # 1.846 s
total = bar * BARS      # ~29.5 s
N     = int(SR * total)

buf   = [0.0] * N

# ─── Core oscillators ────────────────────────────────────────────────────────

def adsr_env(i, total_samples, a, d, s_level, r):
    """Standard ADSR envelope."""
    a_s = int(a * SR);  d_s = int(d * SR);  r_s = int(r * SR)
    s_s = max(0, total_samples - a_s - d_s - r_s)
    if   i < a_s:                     return i / max(1, a_s)
    elif i < a_s + d_s:               return 1.0 - (1.0 - s_level) * (i - a_s) / max(1, d_s)
    elif i < a_s + d_s + s_s:         return s_level
    else:
        t = i - a_s - d_s - s_s
        return max(0.0, s_level * (1.0 - t / max(1, r_s)))

def fm(t0, fc, fm_ratio, index, dur_s, amp, a=0.005, d=0.05, s=0.7, r=0.08):
    """FM synthesis: sin(2π·fc·t + index·sin(2π·fm·t))"""
    start = int(t0 * SR)
    ns    = int(dur_s * SR)
    fm_f  = fc * fm_ratio
    for i in range(min(ns, N - start)):
        t   = i / SR
        env = adsr_env(i, ns, a, d, s, r) * amp
        mod = index * math.sin(2 * math.pi * fm_f * t)
        buf[start + i] += math.sin(2 * math.pi * fc * t + mod) * env

def sine(t0, freq, dur_s, amp, decay=12.0):
    start = int(t0 * SR)
    ns    = int(dur_s * SR)
    for i in range(min(ns, N - start)):
        t = i / SR
        buf[start + i] += math.sin(2 * math.pi * freq * t) * math.exp(-t * decay) * amp

def noise(t0, dur_s, amp, hp=False):
    start = int(t0 * SR)
    ns    = int(dur_s * SR)
    prev  = 0.0
    for i in range(min(ns, N - start)):
        t   = i / SR
        env = math.exp(-t * (30 if dur_s < 0.05 else 12))
        r   = random.uniform(-1, 1)
        if hp:
            r = r - 0.97 * prev
            prev = r
        buf[start + i] += r * env * amp

# ─── Drum kit ────────────────────────────────────────────────────────────────

def kick(t0, amp=1.0):
    """909-style: pitch-swept sine + transient click."""
    start = int(t0 * SR)
    ns    = int(0.28 * SR)
    for i in range(min(ns, N - start)):
        t    = i / SR
        freq = 45 + 130 * math.exp(-t * 24)   # 175→45 Hz sweep
        env  = math.exp(-t * 7)
        buf[start + i] += math.sin(2 * math.pi * freq * t) * env * amp * 1.2
    noise(t0, 0.010, amp * 0.30)

def snare(t0, amp=0.85):
    noise(t0, 0.13, amp * 0.65)
    sine(t0, 180, 0.08, amp * 0.28, decay=32)
    sine(t0, 310, 0.06, amp * 0.14, decay=45)

def clap(t0, amp=0.55):
    for dl in (0.0, 0.006, 0.013):
        noise(t0 + dl, 0.07, amp * 0.38)

def hihat(t0, amp=0.20, open_=False):
    noise(t0, 0.11 if open_ else 0.022, amp, hp=True)

# ─── Scale: A natural minor ──────────────────────────────────────────────────
S = {
    'A1':  55.00, 'E2':  82.41, 'F2':  87.31, 'G2':  98.00,
    'A2': 110.00, 'B2': 123.47, 'C3': 130.81, 'D3': 146.83,
    'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00,
    'B3': 246.94, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63,
    'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'C5': 523.25,
}

# ─── Instruments ─────────────────────────────────────────────────────────────

def bass(n, t0, beats=1.0, amp=0.50):
    """Punchy FM bass — carrier=note, mod=note*2, index=3.5"""
    fm(t0, S[n], 2.0, 3.5, beats * beat, amp, a=0.003, d=0.04, s=0.55, r=0.05)

def arp(n, t0, beats=0.45, amp=0.24):
    """Bright sawtooth-ish arp via FM + 2nd harmonic."""
    fm(t0, S[n], 1.5, 2.0, beats * beat, amp * 0.7, a=0.003, d=0.03, s=0.6, r=0.05)
    fm(t0, S[n], 3.0, 0.7, beats * beat, amp * 0.3, a=0.003, d=0.03, s=0.5, r=0.05)

def lead(n, t0, beats=1.0, amp=0.24):
    """FM lead with slight vibrato character."""
    fm(t0, S[n], 0.50, 2.5, beats * beat, amp * 0.75, a=0.020, d=0.06, s=0.75, r=0.12)
    fm(t0, S[n], 2.00, 0.9, beats * beat, amp * 0.45, a=0.015, d=0.05, s=0.60, r=0.10)

def pad(root_hz, t0, beats=4.0, amp=0.07):
    """Slow-attack pad chord (root + 5th + octave)."""
    for ratio, vol in [(1.0, 1.0), (1.498, 0.55), (2.0, 0.30), (2.5, 0.18)]:
        fm(t0, root_hz * ratio, 0.5, 0.4, beats * beat, amp * vol, a=0.35, d=0.1, s=0.9, r=0.6)

# ─── Patterns ────────────────────────────────────────────────────────────────

BASS_2BAR = [           # (note, beat_offset, duration_beats, amp_scale)
    ('A2', 0.00, 0.85, 1.0), ('A2', 1.00, 0.35, 0.80), ('G2', 1.50, 0.35, 0.75),
    ('A2', 2.00, 0.85, 1.0), ('E2', 3.00, 0.80, 0.90),
    ('F2', 4.00, 0.85, 0.90), ('F2', 5.00, 0.35, 0.75), ('G2', 5.50, 0.35, 0.70),
    ('A2', 6.00, 1.70, 0.85),
]
ARP_BAR = ['A3','C4','E3','G3', 'A3','E3','D3','C3']

LEAD_2BAR = [
    ('A4', 0.00, 0.80, 1.00), ('G4', 0.75, 0.30, 0.85),
    ('F4', 1.25, 0.30, 0.85), ('E4', 1.75, 0.25, 0.80),
    ('D4', 2.00, 0.55, 0.90), ('E4', 2.75, 0.25, 0.80),
    ('C4', 3.00, 1.50, 0.95), ('A3', 4.75, 0.25, 0.70),
    ('B3', 5.00, 0.45, 0.80), ('C4', 5.50, 0.40, 0.80),
    ('A3', 6.00, 0.90, 0.90), ('G3', 7.00, 0.45, 0.75),
    ('A3', 7.50, 0.45, 0.85),
]
PAD_ROOTS = [S['A2'], S['F2'], S['G2'], S['A2']]

# ─── Build track ─────────────────────────────────────────────────────────────

for b in range(BARS):
    t0 = b * bar

    # ── Drums ─────────────────────────────────────────────────────────────────
    kick(t0);  kick(t0 + beat * 2)
    snare(t0 + beat);  snare(t0 + beat * 3)
    hihat(t0 + beat * 3.5, open_=True, amp=0.30)
    for i in range(8):
        hihat(t0 + i * beat * 0.5, amp=0.22 if i % 2 == 0 else 0.14)
    if b >= 4:
        kick(t0 + beat * 1, amp=0.70)
        kick(t0 + beat * 3, amp=0.70)
    if b >= 8:
        clap(t0 + beat);  clap(t0 + beat * 3)

    # ── Bass (all bars) ───────────────────────────────────────────────────────
    offset_beats = (b % 2) * 4
    for n, boff, dur, ascl in BASS_2BAR:
        ab = boff - offset_beats
        if 0 <= ab < 4:
            bass(n, t0 + ab * beat, dur, 0.50 * ascl)

    # ── Pad (bar 2+) ─────────────────────────────────────────────────────────
    if b >= 2:
        pad(PAD_ROOTS[b % 4], t0, beats=4.0, amp=0.075)

    # ── Arp (bar 4+) ─────────────────────────────────────────────────────────
    if b >= 4:
        amp_a = 0.22 + 0.06 * (b >= 12)
        for i, n in enumerate(ARP_BAR):
            arp(n, t0 + i * beat * 0.5, beats=0.45, amp=amp_a)

    # ── Lead (bar 9+) ─────────────────────────────────────────────────────────
    if b >= 8:
        o = (b % 2) * 4
        amp_l = 0.26 + 0.06 * (b >= 12)
        for n, boff, dur, ascl in LEAD_2BAR:
            ab = boff - o
            if 0 <= ab < 4:
                lead(n, t0 + ab * beat, dur, amp_l * ascl)

# ─── Reverb (3-tap echo) ─────────────────────────────────────────────────────
print("  Applying reverb...", end=" ", flush=True)
for delay_ms, decay in [(58, 0.26), (115, 0.16), (210, 0.09)]:
    d = int(SR * delay_ms / 1000)
    for i in range(N - d):
        buf[i + d] += buf[i] * decay
print("OK")

# ─── Normalize + fade-in ─────────────────────────────────────────────────────
mx = max(abs(x) for x in buf) or 1.0
fi = SR // 8    # 0.125s fade-in
for i in range(N):
    buf[i] = max(-1.0, min(1.0, buf[i] / mx))
    if i < fi:
        buf[i] *= i / fi

# ─── Write WAV ───────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "assets", "sounds", "music.wav")
with wave.open(out, "w") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    frames = bytearray()
    for s in buf:
        v = max(-32767, min(32767, int(s * 32767)))
        frames += struct.pack("<h", v) * 2   # stereo
    wf.writeframes(bytes(frames))

print(f"  music.wav: {os.path.getsize(out)/1024/1024:.1f} MB, {total:.1f}s loop")
