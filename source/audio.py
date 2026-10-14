"""Procedural score + SFX for COLLAGE BREAKOUT (25.0 s, 48 kHz stereo)."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 25.0
N = int(SR * DUR)
L = np.zeros(N); Rr = np.zeros(N)
rng = np.random.default_rng(42)
BEAT = 0.5  # 120 BPM

def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N: return
    sig = sig[:N - i0] * gain
    if i0 < 0:
        sig = sig[-i0:]; i0 = 0
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    L[i0:i0 + len(sig)] += sig * l * 1.414
    Rr[i0:i0 + len(sig)] += sig * r * 1.414

def tt(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def noise(d): return rng.standard_normal(int(d * SR))
def midi(m): return 440 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------- instruments
def pluck(f, d=0.6, bright=1.0):
    t = tt(d)
    s = np.zeros_like(t)
    for k in range(1, 7):
        s += np.sin(2 * np.pi * f * k * t + rng.uniform(0, 1)) / k ** 1.4 * np.exp(-t * (5 + 7 * k / bright))
    att = np.minimum(1, t / 0.003)
    return s * att * 0.5

def bass(f, d=0.45, drive=1.5):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 3.0) * np.minimum(1, (d - t) / 0.03)
    return np.tanh(drive * s) * env * 0.6

def pad(freqs, d, cutoff=1800):
    t = tt(d)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ph = 2 * np.pi * f * 2 ** (det / 12) * t + rng.uniform(0, 6)
            s += (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.25
    s = lp(s, cutoff)
    env = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.5)
    return s * env / len(freqs)

def kick(gain=1.0):
    t = tt(0.45)
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7) + 0.25 * hp(noise(0.45), 2000) * np.exp(-t * 200)
    return s * gain

def clap():
    s = np.zeros(int(0.3 * SR))
    for k, off in enumerate((0, 0.011, 0.023)):
        n = bp(noise(0.3), 900, 4500) * np.exp(-tt(0.3) * (60 if k < 2 else 16))
        i = int(off * SR); s[i:] += n[:len(s) - i]
    return s * 0.35

def hat(d=0.06):
    return hp(noise(d), 7000) * np.exp(-tt(d) * 70) * 0.18

def click(freq=2500, d=0.04, q=0.35):
    t = tt(d)
    return (bp(noise(d), freq * (1 - q), freq * (1 + q)) * np.exp(-t * 180)
            + 0.4 * np.sin(2 * np.pi * freq * 0.5 * t) * np.exp(-t * 120))

def swish(d, f0, f1, gain=1.0):
    t = tt(d)
    n = noise(d)
    out = np.zeros_like(n)
    seg = int(0.01 * SR)
    for i in range(0, len(n), seg):     # moving band-pass
        fc = f0 * (f1 / f0) ** (i / len(n))
        out[i:i + seg] = bp(n[max(0, i - 4 * seg):i + seg], fc * 0.6, min(fc * 1.6, SR / 2 - 100))[-len(n[i:i + seg]):]
    env = np.sin(np.pi * t / d) ** 2
    return out * env * gain

def rustle(d, rate=18, lo=1500, hi=7000):
    t = tt(d)
    am = np.abs(np.convolve(rng.standard_normal(len(t)), np.ones(int(SR / rate)) / (SR / rate), 'same'))
    am = am / (am.max() + 1e-9)
    return bp(noise(d), lo, hi) * am * np.sin(np.pi * t / d) * 0.6

def squeak(f0, f1, d, vib=9):
    t = tt(d)
    f = f0 * (f1 / f0) ** (t / d) * (1 + 0.025 * np.sin(2 * np.pi * vib * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    env = np.sin(np.pi * np.minimum(t / d, 1)) ** 1.5
    return s * env * 0.25

def boom():
    t = tt(2.0)
    f = 32 + 40 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    n = lp(noise(2.0), 1800) * np.exp(-t * 4.5) * 0.7
    crack = hp(noise(2.0), 1500) * np.exp(-t * 25) * 0.6
    return np.tanh(1.6 * (s + n + crack))

# ------------------------------------------------------------- score
CH = [[53, 57, 60, 64], [57, 60, 64, 67], [58, 62, 65, 69], [60, 64, 67, 70]]   # Fmaj7 Am7 Bbmaj7 C7
ROOT = [41, 45, 46, 48]
PENT = [65, 67, 69, 72, 74, 77, 79, 81]

def chord_at(t): return int(t // 2.0) % 4

# 0-2 s: near silence, a faint high pad breath
add(pad([midi(77), midi(81)], 2.2, 2500), 0.0, 0.04)

# 2-11 s: curious plucks + soft bass
motif = [0, None, 2, None, 4, 3, None, 1, 0, None, 3, None, 5, 4, None, 2]
for i in range(int((11.0 - 2.0) / (BEAT / 2))):
    t0 = 2.0 + i * BEAT / 2
    step = motif[i % 16]
    if step is None: continue
    build = (t0 - 2.0) / 9.0
    if i < 8 and i % 4: continue          # very sparse at first
    add(pluck(midi(PENT[step]), 0.5), t0, 0.16 + 0.12 * build, pan=0.3 * np.sin(i))
for b in range(int((11.0 - 4.0) / 2.0) + 1):
    t0 = 4.0 + b * 2.0
    add(bass(midi(ROOT[chord_at(t0)]), 0.9), t0, 0.35)
for i in range(int((13.0 - 6.0) / (BEAT / 2))):     # shaker from 6 s
    t0 = 6.0 + i * BEAT / 2
    add(hp(noise(0.05), 5000) * np.exp(-tt(0.05) * 60), t0, 0.05 + 0.03 * ((i % 2) == 1), pan=0.4)
add(pad([midi(m) for m in CH[0]], 9.0, 1200), 2.0, 0.07)

# 11-13: tension — sixteenth plucks, rising noise, low note at 11.5
for i in range(int(2.0 / (BEAT / 4))):
    t0 = 11.0 + i * BEAT / 4
    add(pluck(midi(PENT[(i * 3) % 5] + (12 if i % 4 == 3 else 0)), 0.25, 1.4), t0, 0.12 + 0.06 * i / 8, pan=0.2 * ((-1) ** i))
add(bass(midi(38), 1.5, 2.0) * np.minimum(1, tt(1.5) / 1.2) * 1.6, 11.5, 0.5)
riser = bp(noise(1.5), 400, 3000) * (tt(1.5) / 1.5) ** 2.5
add(riser, 11.5, 0.12)

# 13.7-14: reverse swell into the hit
sw = hp(noise(0.3), 1500) * (tt(0.3) / 0.3) ** 3
add(sw, 13.7, 0.35)

# 14-23: the beat
for i in range(int((23.0 - 14.0) / BEAT)):
    t0 = 14.0 + i * BEAT
    add(kick(), t0, 0.75 if i else 0.0)
    if i % 2 == 1: add(clap(), t0, 0.8, pan=0.05)
    add(hat(), t0 + BEAT / 2, 1.0, pan=-0.3)
    if i % 4 == 3: add(hat(0.03), t0 + 3 * BEAT / 4, 0.8, pan=0.3)
for i in range(int((23.0 - 14.0) / (BEAT / 2))):
    t0 = 14.0 + i * BEAT / 2
    c = chord_at(t0)
    add(bass(midi(ROOT[c] + (12 if i % 4 == 2 else 0)), 0.22, 2.2), t0, 0.42)
for i in range(int((23.0 - 14.5) / (BEAT / 4))):
    t0 = 14.5 + i * BEAT / 4
    c = chord_at(t0)
    note = CH[c][[0, 2, 1, 3, 2, 1, 3, 2][i % 8]] + 12
    add(pluck(midi(note), 0.3, 1.6), t0, 0.10, pan=0.5 * np.sin(i * 0.7))
for b in range(5):
    t0 = 14.0 + b * 2.0
    add(pad([midi(m) for m in CH[chord_at(t0)]], 2.1, 2200), t0, 0.08)

# 23-25: resolution
add(pad([midi(m) for m in (53, 57, 60, 64, 67)], 2.0, 2600) , 23.5, 0.16)
for k, m in enumerate((65, 69, 72, 76, 79)):
    add(pluck(midi(m), 1.5, 0.8), 24.0 + k * 0.06, 0.16, pan=-0.4 + 0.2 * k)
add(bass(midi(41), 1.0, 1.2), 24.0, 0.45)
add(kick(0.8), 24.0, 0.6)

# ------------------------------------------------------------- SFX
add(squeak(600, 1250, 0.07, vib=0) * 1.5, 2.0, 0.5, pan=-0.5)        # curiosity pop
add(pluck(midi(84), 0.25, 2.0), 2.02, 0.15, pan=-0.5)
for t0 in (2.45, 2.95, 3.45):                                          # tiny fabric moves
    add(rustle(0.3, 30, 800, 3000), t0, 0.12, pan=-0.6)
add(rustle(0.5, 25, 900, 4000), 4.1, 0.15, pan=-0.6)
add(click(2600, 0.05), 4.5, 0.55, pan=-0.6)                           # fingertip taps
add(click(2400, 0.05), 4.85, 0.35, pan=-0.6)
add(squeak(1300, 900, 0.18), 5.05, 0.3, pan=-0.6)                    # boundary springs back
add(rustle(0.4, 22), 6.1, 0.18, pan=-0.6)
add(squeak(650, 1150, 0.42), 6.5, 0.45, pan=-0.6)                    # elastic paper squeak
add(squeak(1100, 750, 0.25), 7.4, 0.3, pan=-0.6)
add(rustle(0.6, 40, 2500, 9000), 6.9, 0.14, pan=-0.6)                 # objects tremble
add(squeak(240, 400, 0.65, vib=6) * 1.4, 9.0, 0.5, pan=-0.6)          # deeper stretch
add(bp(noise(0.7), 200, 900) * np.sin(np.pi * tt(0.7) / 0.7), 9.0, 0.12, pan=-0.6)
add(squeak(420, 260, 0.3, vib=6), 10.0, 0.35, pan=-0.6)
add(rustle(0.4, 30), 10.5, 0.15, pan=-0.6)
add(squeak(300, 600, 0.5, vib=7) * 1.4, 11.5, 0.45, pan=-0.6)         # final big push
# 12.0 crack
snap = hp(noise(0.25), 2500) * np.exp(-tt(0.25) * 40)
add(snap, 12.0, 0.9, pan=-0.5)
add(click(4200, 0.03, 0.5), 12.0, 0.8, pan=-0.5)
for k in range(28):
    tk = 12.02 + (k / 28) ** 1.6 * 0.95 + rng.uniform(-0.01, 0.01)
    add(click(rng.uniform(3000, 7000), 0.015, 0.4), tk, rng.uniform(0.08, 0.3) * (1 - k / 40), pan=-0.5 + rng.uniform(-0.15, 0.15))
# 13.0-13.7: music drops out, a lone fragment falls
add(rustle(0.6, 14, 1200, 5000), 13.05, 0.22, pan=-0.4)
add(click(1800, 0.04), 13.65, 0.35, pan=-0.4)
add(click(2200, 0.03), 13.78, 0.12, pan=-0.4)
buzz = np.sin(2 * np.pi * 60 * tt(0.45)) * (tt(0.45) / 0.45) ** 2 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * tt(0.45))))
add(lp(buzz, 400), 13.55, 0.18, pan=-0.5)
# 14.0 explosion
add(boom(), 14.0, 1.0, pan=-0.2)
add(swish(0.9, 6000, 400, 1.0), 14.0, 0.5, pan=-0.3)
for k in range(60):                                                    # paper burst crinkles
    tk = 14.0 + rng.exponential(0.18)
    add(click(rng.uniform(1500, 6000), 0.02, 0.5), tk, rng.uniform(0.05, 0.25), pan=rng.uniform(-0.9, 0.9))
add(rustle(1.6, 35, 1500, 8000), 14.05, 0.35, pan=0.0)                 # fluttering pages
add(swish(0.6, 500, 3500), 14.08, 0.45, pan=-0.7)                      # camera to upper-left
for k in range(5):
    add(click(3300 + 300 * k, 0.03, 0.15), 14.12 + 0.045 * k, 0.25, pan=-0.7)   # camera rattle
add(swish(0.7, 400, 2500), 14.15, 0.4, pan=0.0)                        # lily
t_v = tt(1.0); fv = 180 * (1 + 0.15 * np.sin(2 * np.pi * 3 * t_v))    # vinyl whoosh
vin = np.sin(2 * np.pi * np.cumsum(fv) / SR) * np.sin(np.pi * t_v) ** 2 * 0.3 + swish(1.0, 800, 3000, 0.6)
add(vin, 14.15, 0.45, pan=0.7)
add(rustle(0.7, 24, 1000, 5000), 14.2, 0.3, pan=0.8)                   # ticket flip
for k in range(14):                                                    # butterfly wing flutter
    add(bp(noise(0.06), 300, 1400) * np.sin(np.pi * tt(0.06) / 0.06), 14.5 + k * 0.111, 0.10, pan=-0.3 + 0.08 * k)
for t0, pan in ((14.3, 0.4), (14.45, -0.5), (14.6, 0.6), (15.0, -0.2), (15.5, 0.5)):
    add(swish(0.5, 700, 3000), t0, 0.25, pan=pan)
for t0, pan in ((17.0, -0.4), (18.0, 0.4), (19.0, -0.2), (20.0, 0.3)):  # collage takes over
    add(swish(0.8, 300, 2000), t0, 0.25, pan=pan)
    add(rustle(0.6, 25), t0 + 0.2, 0.12, pan=-pan)
for k in range(12):                                                    # paper placement clicks
    t0 = 20.25 + k * 0.25
    add(click(rng.uniform(1600, 3200), 0.04), t0, 0.35 + 0.15 * (k % 2), pan=rng.uniform(-0.7, 0.7))
    add(rustle(0.15, 40, 1500, 6000), t0 - 0.06, 0.12, pan=rng.uniform(-0.6, 0.6))
# 23.5 final snap
add(click(2200, 0.06, 0.5), 23.5, 0.8)
add(kick(0.7), 23.5, 0.5)
add(hp(noise(0.12), 1200) * np.exp(-tt(0.12) * 50), 23.5, 0.45)
add(bp(noise(0.06), 300, 1400) * np.sin(np.pi * tt(0.06) / 0.06), 23.3, 0.12, pan=0.6)   # last wing flap
add(bp(noise(0.06), 300, 1400) * np.sin(np.pi * tt(0.06) / 0.06), 23.5, 0.10, pan=0.6)
add(rustle(0.9, 10, 800, 3000), 24.0, 0.10)                           # paper settling

# ------------------------------------------------------------- master
# music dropout window 13.0-13.7 (duck everything except the SFX placed there is not separable,
# so the score above simply has no notes there; the bass drone is cut by an envelope)
mix = np.stack([L, Rr], 1)
t = np.arange(N) / SR
duck = np.ones(N)
m = (t > 13.0) & (t < 13.7)
duck[m] = 1.0
duck = np.convolve(duck, np.ones(480) / 480, 'same')
mix *= duck[:, None]
pre = 1 + 0.7 * (1 - np.clip((t - 13.9) / 0.1, 0, 1))
mix *= pre[:, None]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.abs(mix).max() / 0.89
fade = np.minimum(1, (N - np.arange(N)) / (0.15 * SR))
mix *= fade[:, None]
wavfile.write('audio.wav', SR, (mix * 32767).astype(np.int16))
print('ok', mix.shape)
