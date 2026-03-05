"""Generate a crisp laser-shoot sound effect."""
import wave, struct, math, os

SR  = 44100
dur = 0.13
N   = int(SR * dur)

frames = bytearray()
for i in range(N):
    t     = i / SR
    decay = math.exp(-t * 28)
    # descending FM "pew" tone
    freq  = 1400 - 900 * (t / dur)
    mod   = 3.0 * math.sin(2 * math.pi * freq * 2.8 * t)
    s     = math.sin(2 * math.pi * freq * t + mod) * decay * 0.65
    # add a thin noise transient at the start
    if t < 0.015:
        import random
        s += random.uniform(-0.3, 0.3) * (1 - t / 0.015)
    v = max(-32767, min(32767, int(s * 32767)))
    frames += struct.pack("<h", v) * 2

out = os.path.join(os.path.dirname(__file__), "assets", "sounds", "shoot.wav")
with wave.open(out, "w") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(bytes(frames))
print(f"shoot.wav: {os.path.getsize(out)} bytes")
