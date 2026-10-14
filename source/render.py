"""COLLAGE BREAKOUT — Same Girl, Bigger World.  1080x1920, 24 fps, 600 frames.

usage: python3 render.py video out.mp4        (raw video, no audio)
       python3 render.py stills t1 t2 ...    (PNG previews)
"""
import json, math, os, subprocess, sys
import cv2
import numpy as np

W, H, FPS, NFR = 1080, 1920, 24, 600
SF, OFF = 1.25, np.array([-100.0, 0.0])            # collage -> final frame
IC = np.array([92.0, 1574.0]); R = 49.5             # icon in frame
CC = np.array([511.0, 976.0]); RC = 511.0           # avatar circle in collage
SI = R / RC
PUSH = np.array([0.766, -0.643])                     # push direction (up-right)
PHI_P = math.atan2(PUSH[1], PUSH[0])
WHITE = np.array([254, 254, 254], np.float32) / 255
CREAM = np.array([206, 226, 238], np.float32) / 255  # BGR

# ---------------------------------------------------------------- helpers
def clamp01(x): return min(1.0, max(0.0, x))
def smooth(x): x = clamp01(x); return x * x * (3 - 2 * x)
def smoother(x): x = clamp01(x); return x * x * x * (x * (x * 6 - 15) + 10)
def ease_out(x, p=3.0): x = clamp01(x); return 1 - (1 - x) ** p
def settle(x, c=5.0):
    x = clamp01(x); return smooth(x) + c * x ** 3 * (1 - x) ** 2
def lerp(a, b, t): return a + (b - a) * t

def keyframes(t, keys):
    """keys: list of (t, value); smoothstep between keys (stop-motion-like holds)."""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, smooth((t - t0) / (t1 - t0)))
    return keys[-1][1]

def catmull(t, pts):
    """pts: [(t, x, y)] — Catmull-Rom through points, parameterised by time."""
    ts = [p[0] for p in pts]
    if t <= ts[0]: return np.array(pts[0][1:])
    if t >= ts[-1]: return np.array(pts[-1][1:])
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    P = [np.array(pts[min(max(k, 0), len(pts) - 1)][1:], float) for k in (i - 1, i, i + 1, i + 2)]
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    u2, u3 = u * u, u * u * u
    return 0.5 * ((2 * P[1]) + (-P[0] + P[2]) * u + (2 * P[0] - 5 * P[1] + 4 * P[2] - P[3]) * u2
                  + (-P[0] + 3 * P[1] - 3 * P[2] + P[3]) * u3)

# ---------------------------------------------------------------- layers
class Layer:
    def __init__(self, name, rgba, origin, anchor):
        self.name = name
        self.origin = np.array(origin, float)        # bbox origin in collage
        self.anchor = np.array(anchor, float)        # anchor in layer px
        self.pyr = self.build(rgba)
        self.center = self.origin + self.anchor      # anchor in collage coords

    @staticmethod
    def build(rgba):
        a = rgba[..., 3:4].astype(np.float32) / 255
        im = np.concatenate([rgba[..., :3].astype(np.float32) / 255 * a, a], 2)
        pyr = [im]
        while min(pyr[-1].shape[:2]) > 16 and len(pyr) < 7:
            h, w = pyr[-1].shape[:2]
            pyr.append(cv2.resize(pyr[-1], (max(1, w // 2), max(1, h // 2)), interpolation=cv2.INTER_AREA))
        return pyr

def pose_matrix(layer, pos, s, rot=0.0, sx=1.0, beta=0.0):
    """layer px -> frame px.  sx scales along local axis rotated by beta (flap / flip)."""
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    Rm = np.array([[c, -sn], [sn, c]])
    cb, sb = math.cos(math.radians(beta)), math.sin(math.radians(beta))
    Bm = np.array([[cb, -sb], [sb, cb]])
    A = s * Rm @ Bm @ np.diag([sx, 1.0]) @ Bm.T
    t = np.array(pos) - A @ layer.anchor
    return np.hstack([A, t[:, None]])

def draw(canvas, layer, M, view=(1.0, 0.0, 0.0), shadow=None, amul=None, img_override=None):
    """Composite layer onto canvas (opaque BGR float). view=(k,ox,oy): canvas=k*(frame-o)."""
    k, ox, oy = view
    Mc = M.copy() * k
    Mc[:, 2] = k * (M[:, 2] - np.array([ox, oy]))
    sc = math.sqrt(abs(np.linalg.det(Mc[:, :2])))
    pyr = img_override if img_override is not None else layer.pyr
    L = 0
    while L + 1 < len(pyr) and sc * (2 ** (L + 1)) <= 1.0:
        L += 1
    f = 2 ** L
    img = pyr[L]
    ML = Mc.copy()
    ML[:, :2] = Mc[:, :2] * f
    ML[:, 2] = Mc[:, 2] + Mc[:, :2] @ np.array([(f - 1) / 2, (f - 1) / 2])
    h, w = img.shape[:2]
    corners = ML[:, :2] @ np.array([[0, w, 0, w], [0, 0, h, h]]) + ML[:, 2:3]
    ch, cw = canvas.shape[:2]
    x0 = max(0, int(math.floor(corners[0].min())) - 1); x1 = min(cw, int(math.ceil(corners[0].max())) + 2)
    y0 = max(0, int(math.floor(corners[1].min())) - 1); y1 = min(ch, int(math.ceil(corners[1].max())) + 2)
    if x1 <= x0 or y1 <= y0:
        return
    M2 = ML.copy(); M2[:, 2] -= [x0, y0]
    dst = cv2.warpAffine(img, M2, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    if amul is not None:
        m = amul(x0, y0, x1, y1)
        dst *= m[..., None]
    a = dst[..., 3:4]
    if shadow is not None and shadow[3] > 0.003:
        dx, dy, sig, op = shadow
        pad = int(3 * sig + abs(dx) + abs(dy)) + 2
        sx0, sy0 = max(0, x0 - pad), max(0, y0 - pad)
        sx1, sy1 = min(cw, x1 + pad), min(ch, y1 + pad)
        sh = np.zeros((sy1 - sy0, sx1 - sx0), np.float32)
        Ms = np.float32([[1, 0, x0 - sx0 + dx], [0, 1, y0 - sy0 + dy]])
        sh = cv2.warpAffine(a[..., 0], Ms, (sx1 - sx0, sy1 - sy0))
        if sig > 0.3:
            sh = cv2.GaussianBlur(sh, (0, 0), sig)
        canvas[sy0:sy1, sx0:sx1] *= (1 - op * sh)[..., None]
    reg = canvas[y0:y1, x0:x1]
    reg *= (1 - a)
    reg += dst[..., :3]

# ---------------------------------------------------------------- load assets
def load():
    meta = json.load(open('layers/layers.json'))
    layers = {}
    for m in meta:
        rgba = cv2.imread(f"layers/{m['name']}.png", cv2.IMREAD_UNCHANGED)
        x0, y0 = m['bbox'][:2]
        anchor = np.array(m['center']) - [x0, y0]
        if m['name'] == 'butterfly':
            anchor = np.array([828.0, 815.0]) - [x0, y0]   # body
        layers[m['name']] = Layer(m['name'], rgba, (x0, y0), anchor)
    order = [m['name'] for m in sorted(meta, key=lambda m: m['z'])]
    bg = cv2.imread('layers/bg.png')
    bgl = Layer('bg', np.dstack([bg, np.full(bg.shape[:2], 255, np.uint8)]), (0, 0), (512.0, 768.0))
    # ticket back side: plain cream paper with grain
    tk = cv2.imread('layers/ticket.png', cv2.IMREAD_UNCHANGED)
    g = cv2.GaussianBlur(np.random.default_rng(5).normal(0, 7, tk.shape[:2]).astype(np.float32), (0, 0), 1)
    back = np.clip(np.array([196, 214, 226], np.float32) + g[..., None], 0, 255).astype(np.uint8)
    layers['ticket'].back = Layer.build(np.dstack([back, tk[..., 3]]))
    # woman rgba kept for the smile warp
    layers['woman'].rgba = cv2.imread('layers/woman.png', cv2.IMREAD_UNCHANGED)
    return layers, order, bgl

LAYERS, ORDER, BG = load()
ELEMS = [n for n in ORDER if n != 'woman']

def final_pos(l): return SF * l.center + OFF
def icon_pos(l): return SI * (l.center - CC) + IC

# ---------------------------------------------------------------- woman puppet (0-14 s)
LEAN = [(0, 0), (2.0, 0), (2.4, -6), (3.8, -6), (4.0, 4), (4.6, 22), (5.0, 34), (5.4, 28), (6.0, 18),
        (6.4, 42), (6.9, 70), (7.4, 60), (7.8, 38), (8.5, 30), (9.0, 82), (9.6, 98), (10.0, 88),
        (10.4, 22), (10.8, -18), (11.0, -30), (11.5, 62), (12.0, 125), (12.25, 55), (12.6, 28), (13.0, 24), (14.0, 24)]
ROT = [(0, 0), (2.0, 0), (2.4, -4), (2.9, 4), (3.4, 4), (3.8, 0), (4.6, 2), (5.0, 3), (6.0, 1),
       (6.4, 3), (6.9, 5), (7.4, 4), (7.8, 2), (8.5, 4), (9.0, 10), (9.6, 11), (10.0, 10), (10.4, 3),
       (10.8, -2), (11.0, -3), (11.5, 4), (12.0, 6), (12.25, 0), (12.6, -2), (13.0, 3), (13.6, 4), (14.0, 4)]
LIFT = [(0, 0), (2.0, 0), (2.5, -22), (3.6, -22), (4.0, -8), (11.95, -8), (12.1, -26), (12.4, -8), (14, -8)]
BULGE = [(0, 0), (4.6, 0), (5.0, .045), (5.4, 0), (6.4, .05), (6.9, .11), (7.4, .085), (7.8, 0),
         (8.5, 0), (9.0, .13), (9.6, .175), (10.0, .155), (10.4, .02), (11.0, 0), (11.5, .10),
         (12.0, .24), (12.25, .06), (13.0, .035), (14.0, .035)]

def bulge_amount(t):
    A = keyframes(t, BULGE)
    for tr, a0 in ((5.4, .03), (7.8, .045), (10.4, .05), (12.25, .05)):
        if t > tr:
            A += a0 * math.exp(-(t - tr) / 0.16) * math.sin(2 * math.pi * 6 * (t - tr))
    return max(A, -0.03)

def woman_icon_pose(t):
    l = LAYERS['woman']
    lean = keyframes(t, LEAN)
    lift = keyframes(t, LIFT)
    pos = icon_pos(l) + SI * (lean * PUSH + np.array([0, lift]))
    hop = 1 + 0.04 * math.exp(-((t - 12.1) / 0.12) ** 2)
    return pos, SI * hop, keyframes(t, ROT)

TREMBLE = {'lily': 0.0, 'camera': 1.3, 'butterfly': 2.1, 'note_good': 3.0, 'note_same': 4.2, 'ticket': 5.1}
def tremble(t, name):
    if name not in TREMBLE: return 0.0
    env = (math.exp(-((t - 7.0) / 0.45) ** 2) + 1.2 * math.exp(-((t - 9.5) / 0.5) ** 2)
           + 1.8 * math.exp(-((t - 12.1) / 0.35) ** 2) + 0.8 * math.exp(-((t - 13.8) / 0.2) ** 2))
    return 4.0 * env * math.sin(2 * math.pi * 9 * t + TREMBLE[name])

# ---------------------------------------------------------------- crack geometry (unit circle)
def make_cracks():
    rng = np.random.default_rng(11)
    P0 = 0.97 * np.array([math.cos(PHI_P), math.sin(PHI_P)])
    lines = []   # (points Nx2, t_start, t_end, width)
    for k in range(6):          # impact star
        ang = PHI_P + math.pi + rng.uniform(-1.4, 1.4)
        L = rng.uniform(0.07, 0.2)
        pts = [P0]
        for j in range(1, 5):
            ang += rng.uniform(-0.4, 0.4)
            pts.append(pts[-1] + (L / 4) * np.array([math.cos(ang), math.sin(ang)]))
        lines.append((np.array(pts), 0.0, 0.12, 2))
    for direction, span in ((1, 2.6), (-1, 2.2)):   # perimeter branches
        pts = []; phi = PHI_P; r = 0.95
        while abs(phi - PHI_P) < span:
            r = float(np.clip(r + rng.uniform(-0.025, 0.025), 0.88, 0.985))
            pts.append(r * np.array([math.cos(phi), math.sin(phi)]))
            phi += direction * rng.uniform(0.05, 0.11)
        pts = np.array(pts)
        lines.append((pts, 0.05, 1.0, 2))
        n = len(pts)
        for j in range(4, n - 2, 5):   # inward sub-branches
            frac = j / n
            q = [pts[j]]
            ang = math.atan2(-pts[j][1], -pts[j][0]) + rng.uniform(-0.8, 0.8)
            for _ in range(rng.integers(2, 5)):
                ang += rng.uniform(-0.5, 0.5)
                q.append(q[-1] + rng.uniform(0.03, 0.06) * np.array([math.cos(ang), math.sin(ang)]))
            ts = 0.05 + 0.95 * frac
            lines.append((np.array(q), ts, min(1.0, ts + 0.25), 1))
    return lines
CRACKS = make_cracks()

def crack_progress(t):
    if t < 12.0: return 0.0
    return 0.12 * smooth((t - 12.0) / 0.08) + 0.88 * ease_out((t - 12.08) / 0.9, 2.2)

NOTCH = None
def notch_poly():
    rng = np.random.default_rng(4)
    pts = []
    for a in np.linspace(-0.11, 0.11, 6):
        pts.append(1.02 * np.array([math.cos(PHI_P + a), math.sin(PHI_P + a)]))
    for a in np.linspace(0.11, -0.11, 5):
        r = 0.80 + rng.uniform(-0.03, 0.03)
        pts.append(r * np.array([math.cos(PHI_P + a), math.sin(PHI_P + a)]))
    return np.array(pts)
NOTCH = notch_poly()

# ---------------------------------------------------------------- icon patch (0-14 s)
PK, PH = 4, 70                       # supersampling, patch half-size (frame px)
PS = 2 * PH * PK
PO = IC - PH                         # patch origin in frame
yy, xx = np.mgrid[0:PS, 0:PS].astype(np.float32) + 0.5
PRHO = np.hypot(xx - PS / 2, yy - PS / 2)
PPHI = np.arctan2(yy - PS / 2, xx - PS / 2)
RCV = R * PK

def ang_gauss(phi, sig=0.55):
    d = np.angle(np.exp(1j * (phi - PHI_P)))
    return np.exp(-(d / sig) ** 2)
PG = ang_gauss(PPHI).astype(np.float32)

def render_icon_content(t, freeze_t=None):
    tt = t if freeze_t is None else freeze_t
    canvas = np.empty((PS, PS, 3), np.float32); canvas[:] = WHITE
    view = (PK, PO[0], PO[1])
    draw(canvas, BG, pose_matrix(BG, icon_pos(BG), SI), view)
    for n in ELEMS:
        l = LAYERS[n]
        draw(canvas, l, pose_matrix(l, icon_pos(l), SI, tremble(tt, n)), view)
    pos, s, rot = woman_icon_pose(tt)
    draw(canvas, LAYERS['woman'], pose_matrix(LAYERS['woman'], pos, s, rot), view)
    A = bulge_amount(tt)
    if abs(A) > 1e-4:
        fac = 1 + A * PG * np.clip(PRHO / RCV, 0, 1) ** 2
        src = PRHO / fac
        mx = (PS / 2 + src * np.cos(PPHI)).astype(np.float32)
        my = (PS / 2 + src * np.sin(PPHI)).astype(np.float32)
        canvas = cv2.remap(canvas, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return canvas, A

def to_patch(pts, A):
    phi = np.arctan2(pts[:, 1], pts[:, 0])
    fac = 1 + A * ang_gauss(phi) * np.clip(np.hypot(pts[:, 0], pts[:, 1]), 0, 1) ** 2
    return (PS / 2 + pts * fac[:, None] * RCV)

def icon_alpha(A, notch):
    edge = RCV * (1 + A * PG)
    a = np.clip(edge - PRHO + 0.5, 0, 1).astype(np.float32)
    if notch:
        m = np.zeros((PS, PS), np.uint8)
        cv2.fillPoly(m, [np.round(to_patch(NOTCH, A) * 8).astype(np.int32)], 255, cv2.LINE_AA, shift=3)
        a *= 1 - m.astype(np.float32) / 255
    return a

def draw_cracks(canvas, t, A):
    p = crack_progress(t)
    if p <= 0: return
    glow = 1.0 + 0.6 * smooth((t - 13.5) / 0.5)
    for pts, t0, t1, wdt in CRACKS:
        q = clamp01((p - t0) / (t1 - t0))
        if q <= 0: continue
        n = max(2, int(math.ceil(q * len(pts))))
        seg = pts[:n].copy()
        if q < 1 and n >= 2:
            frac = q * len(pts) - (n - 1)
            seg[-1] = seg[-2] + (seg[-1] - seg[-2]) * clamp01(frac)
        P = np.round(to_patch(seg, A) * 8).astype(np.int32)
        th = max(1, int(round(wdt * glow)))
        cv2.polylines(canvas, [P + 8 * 2], False, (0.98, 0.98, 0.98), th + 1, cv2.LINE_AA, shift=3)
        cv2.polylines(canvas, [P], False, (0.25, 0.24, 0.24), th, cv2.LINE_AA, shift=3)

FRAG_CACHE = {}
def fragment_image():
    if 'f' not in FRAG_CACHE:
        content, A = render_icon_content(13.0)
        draw_cracks(content, 13.0, A)
        m = np.zeros((PS, PS), np.uint8)
        cv2.fillPoly(m, [np.round(to_patch(NOTCH, A) * 8).astype(np.int32)], 255, cv2.LINE_AA, shift=3)
        a = m.astype(np.float32) / 255 * icon_alpha(A, False)
        ys, xs = np.nonzero(a > 0)
        y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
        rgba = np.dstack([content[y0:y1, x0:x1] * a[y0:y1, x0:x1, None], a[y0:y1, x0:x1]])
        small = cv2.resize(rgba, ((x1 - x0) // PK + 1, (y1 - y0) // PK + 1), interpolation=cv2.INTER_AREA)
        c = np.array([(x0 + x1) / 2, (y0 + y1) / 2]) / PK + PO
        FRAG_CACHE['f'] = (small, c)
    return FRAG_CACHE['f']

def draw_fragment(frame, t):
    if t < 13.05: return
    img, c0 = fragment_image()
    u = clamp01((t - 13.05) / 0.6)
    pop = PUSH * 7 * ease_out(u * 3, 2)
    fall = np.array([10 * u, 78 * u * u])
    if t > 13.65:   # small bounce on landing
        b = t - 13.65
        fall = np.array([10, 78]) + np.array([2 * smooth(b / .2), -6 * math.exp(-b / .07) * math.sin(min(b / .14, 1) * math.pi)])
    pos = c0 + pop + fall
    rot = 220 * ease_out(u, 1.6) + (8 * math.exp(-(t - 13.65) / .1) * math.sin((t - 13.65) * 40) if t > 13.65 else 0)
    height = 1 - smooth(u) if t < 13.65 else 0
    h, w = img.shape[:2]
    fake = type('L', (), {})(); fake.anchor = np.array([w / 2, h / 2])
    M = pose_matrix(fake, pos, 1.0, rot)
    draw(frame, None, M, shadow=(1 + 5 * height, 2 + 8 * height, 0.6 + 2 * height, 0.35), img_override=[img])

def render_pre(t, fi):
    frame = np.empty((H, W, 3), np.float32); frame[:] = WHITE
    content, A = render_icon_content(t)
    draw_cracks(content, t, A)
    alpha = icon_alpha(A, t >= 13.05)
    rgba = np.dstack([content * alpha[..., None], alpha])
    small = cv2.resize(rgba, (2 * PH, 2 * PH), interpolation=cv2.INTER_AREA)
    jit = np.zeros(2)
    if t > 13.55:
        amp = 1.6 * smooth((t - 13.55) / 0.4)
        jit = np.random.default_rng(fi).uniform(-amp, amp, 2)
    M = np.float32([[1, 0, PO[0] + jit[0]], [0, 1, PO[1] + jit[1]]])
    x0, y0 = int(PO[0]) - 4, int(PO[1]) - 4
    M[:, 2] -= [x0, y0]
    sz = 2 * PH + 8
    dst = cv2.warpAffine(small, M, (sz, sz))
    reg = frame[y0:y0 + sz, x0:x0 + sz]
    reg *= 1 - dst[..., 3:4]
    reg += dst[..., :3]
    draw_fragment(frame, t)
    return frame

# ---------------------------------------------------------------- explosion (14-25 s)
# name: (apex offset from final, apex scale mult, apex rot, spin turns, curve)
APEX = {
    'burj':       ((60, -420), 1.20, 12, 0, .15),
    'eiffel':     ((-170, -360), 1.25, -32, 0, -.2),
    'airplane':   ((-300, -300), 1.30, -18, 0, .25),
    'star_top':   ((-110, -260), 1.40, 200, 0, -.3),
    'leaves':     ((-220, -240), 1.30, -70, 0, .2),
    'heart':      ((-260, -160), 1.35, -45, 0, -.25),
    'headphones': ((240, -360), 1.22, 28, 0, .15),
    'palm':       ((230, -200), 1.25, 38, 0, -.2),
    'orange':     ((170, -340), 1.35, 170, 0, .3),
    'vinyl':      ((260, -320), 1.30, 20, 2, .1),
    'note_good':  ((-250, -120), 1.40, 18, 0, .2),
    'camera':     ((-240, -360), 1.35, -28, 0, -.15),
    'bust':       ((130, -560), 1.30, 15, 0, .1),
    'ocean':      ((-60, -140), 1.10, -8, 0, .1),
    'books':      ((-230, 40), 1.35, -14, 0, .15),
    'ticket':     ((300, 40), 1.30, 20, 0, -.1),
    'hibiscus':   ((260, -80), 1.30, 130, 0, .25),
    'lily':       ((70, -460), 1.60, 50, 0, -.1),
    'flowers':    ((-210, -70), 1.30, -95, 0, .3),
    'star_r':     ((280, 190), 1.40, 210, 0, -.3),
    'star_pink':  ((-230, 120), 1.45, -230, 0, .3),
    'note_same':  ((250, 140), 1.40, -16, 0, -.2),
}
SETTLE_START = {n: 19.8 + 0.9 * ((i * 7) % 11) / 10 for i, n in enumerate(ELEMS)}
DELAY = {n: 0.12 * ((i * 5) % 7) / 6 for i, n in enumerate(ELEMS)}

def start_pose(l):
    p = icon_pos(l)
    d = np.linalg.norm(p - IC)
    s = SI
    if d > 0.7 * R:
        p = IC + (p - IC) * 0.7 * R / d
        s = SI * 0.6
    return p, s

def elem_pose(n, t):
    """returns pos, scale, rot, sx, height(0..1 for shadow)"""
    l = LAYERS[n]
    F = final_pos(l)
    if t >= 23.0:
        return F, SF, 0.0, 1.0, 0.0
    off, sm, rapex, turns, curv = APEX[n]
    off = np.array(off, float)
    S0, s0 = start_pose(l)
    A2 = F + off
    ts = SETTLE_START[n]
    d = DELAY[n]
    tb = clamp01((t - 14.0 - d) / (ts - 14.0 - d))
    E = 0.7 * ease_out(tb, 5.0) + 0.3 * smooth(tb)
    Es = ease_out((t - 14.0 - d) / 2.2, 3.0)
    v = A2 - S0
    perp = np.array([-v[1], v[0]])
    pos = S0 + v * E + perp * curv * math.sin(math.pi * E)
    sA = SF * sm
    scale = math.exp(lerp(math.log(s0), math.log(sA), Es))
    rot = (rapex + 360 * turns) * E
    height = smooth((t - 14.0) / 0.15)
    if t > ts:
        f = settle((t - ts) / (23.0 - ts))
        pos = lerp(A2, F, f)
        scale = math.exp(lerp(math.log(sA), math.log(SF), smooth((t - ts) / (23.0 - ts))))
        rot = 360 * turns + rapex * (1 - f)
        height = 1 - smooth((t - ts) / (23.0 - ts))
    sx = 1.0
    if n == 'ticket':   # one full flip during flight
        sx = math.cos(2 * math.pi * E)
    return pos, scale, rot, sx, height

BF_PATH = None
def butterfly_pose(t):
    l = LAYERS['butterfly']
    F = final_pos(l)
    S0, s0 = start_pose(l)
    if t >= 23.0:
        flap = 1.0
        if 23.25 < t < 23.75:
            flap = 1 - 0.5 * math.sin(math.pi * (t - 23.25) / 0.5)
        return F, SF, 0.0, flap, 0.0
    pts = [(14.0, *S0), (14.6, 330, 1250), (15.6, 590, 860), (16.8, 300, 560), (18.2, 690, 400),
           (19.6, 960, 700), (21.0, F[0] + 40, F[1] - 50), (22.4, F[0], F[1])]
    pos = catmull(t, pts)
    pos2 = catmull(t + 0.04, pts)
    vx = (pos2[0] - pos[0]) / 0.04
    k = smooth((t - 21.4) / 1.0)
    bob = (1 - k) * np.array([0, 10 * math.sin(2 * math.pi * 1.7 * t)])
    pos = pos + bob
    sc_fly = SF * 1.18
    if t < 15.6:
        scale = math.exp(lerp(math.log(s0), math.log(sc_fly), ease_out((t - 14.0) / 1.6, 2.2)))
    else:
        scale = lerp(sc_fly, SF, smooth((t - 20.5) / 1.9))
    rot = (1 - k) * float(np.clip(vx * 0.03, -28, 28))
    flap = 0.25 + 0.75 * abs(math.cos(2 * math.pi * 4.5 * (t - 14.0)))
    flap = lerp(flap, 1.0, smooth((t - 21.9) / 0.5))
    height = (1 - smooth((t - 21.6) / 1.2)) * smooth((t - 14.0) / 0.15)
    return pos, scale, rot, flap, height

def woman_pose(t):
    l = LAYERS['woman']
    p0, s0, r0 = woman_icon_pose(14.0)
    F = final_pos(l)
    u = clamp01((t - 14.0) / 7.8)
    E = ease_out(u, 3.4)
    Es = ease_out(u, 4.0)
    pos = lerp(p0, F, E) + np.array([0, -60]) * math.sin(math.pi * E) * (1 - E)
    scale = math.exp(lerp(math.log(s0), math.log(SF), Es))
    rot = r0 * (1 - E) - 5 * math.sin(math.pi * E) * (1 - E) ** 0.5
    height = smooth((t - 14.0) / 0.2) * (1 - smooth((t - 20.5) / 2.0))
    return pos, scale, rot, height

SMILE_CACHE = {}
def woman_pyr(t):
    a = smooth((t - 23.05) / 0.5)
    if a <= 0: return None
    key = round(a, 3)
    if key in SMILE_CACHE: return SMILE_CACHE[key]
    wl = LAYERS['woman']
    rgba = wl.rgba
    h, w = rgba.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = np.zeros_like(xx); dy = np.zeros_like(yy)
    ox, oy = wl.origin
    for (cx, cy), (mx, my), sig in (((402, 1080), (-3.0, -6.5), 13), ((535, 1087), (3.0, -6.5), 13),
                                    ((395, 1048), (0, -2.2), 26), ((545, 1055), (0, -2.2), 26),
                                    ((468, 1088), (0, -1.2), 22)):
        g = np.exp(-(((xx - (cx - ox)) ** 2 + (yy - (cy - oy)) ** 2) / (2 * sig * sig)))
        dx += a * mx * g; dy += a * my * g
    warped = cv2.remap(rgba, xx - dx, yy - dy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    pyr = Layer.build(warped)[:1]
    SMILE_CACHE.clear(); SMILE_CACHE[key] = pyr
    return pyr

# background reveal (torn turquoise paper)
FY, FX = np.mgrid[0:H, 0:W].astype(np.float32)
FRHO = np.hypot(FX - IC[0], FY - IC[1])
FPHI = np.arctan2(FY - IC[1], FX - IC[0])
def periodic_noise(n, octaves, seed):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 2 * np.pi, n, endpoint=False)
    out = np.zeros(n)
    for f, amp in octaves:
        out += amp * np.sin(f * x + rng.uniform(0, 2 * np.pi))
        out += amp * 0.6 * np.sin((f + 1) * x + rng.uniform(0, 2 * np.pi))
    return out
NB = 4096
N1 = periodic_noise(NB, [(3, .5), (5, .3), (9, .2)], 1)
N2 = periodic_noise(NB, [(23, .5), (41, .3), (77, .25), (131, .2), (233, .15)], 2)
N3 = periodic_noise(NB, [(60, .5), (110, .4), (190, .3)], 3)
PHI_IDX = ((FPHI + np.pi) / (2 * np.pi) * NB).astype(np.int32) % NB

def reveal_radius(t):
    return 50 + 480 * (1 - math.exp(-(t - 14.0) / 0.5)) + 1850 * smooth((t - 14.4) / 6.4)

def render_post(t, fi):
    frame = np.empty((H, W, 3), np.float32); frame[:] = WHITE
    draw_fragment(frame, t)
    # background paper, zooming in from the icon (parallax)
    z = 1 + 0.12 * (1 - ease_out((t - 14.0) / 8.5, 3))
    bpos = IC + z * (final_pos(BG) - IC)
    Rt = reveal_radius(t)
    if Rt < 2700:
        bgc = np.empty((H, W, 3), np.float32); bgc[:] = WHITE
        draw(bgc, BG, pose_matrix(BG, bpos, SF * z))
        edge = Rt * (1 + 0.07 * N1[PHI_IDX]) + 16 * min(1.0, Rt / 500) * N2[PHI_IDX]
        d = edge - FRHO
        rimw = (7 + 3 * N3[PHI_IDX]) * min(1.0, 0.4 + Rt / 400)
        a_rim = np.clip(d + 0.5, 0, 1)
        a_blue = np.clip(d - rimw + 0.5, 0, 1)
        sh = np.clip(1 + d / 22, 0, 1) ** 2 * 0.22 * (d < 0)
        frame *= (1 - sh)[..., None]
        frame += (CREAM - frame) * a_rim[..., None]
        frame += (bgc - frame) * a_blue[..., None]
    else:
        draw(frame, BG, pose_matrix(BG, bpos, SF * z))
    # clip mask: collage bursts out of the circle during the first instants
    rclip = R + 2200 * ease_out((t - 14.0) / 0.4, 2.5)
    amul = None
    if rclip < 2000:
        amul = lambda x0, y0, x1, y1: np.clip(rclip - FRHO[y0:y1, x0:x1] + 0.5, 0, 1)
    for n in ELEMS:
        l = LAYERS[n]
        if n == 'butterfly':
            continue
        pos, sc, rot, sx, hgt = elem_pose(n, t)
        img = None
        if n == 'ticket' and sx < 0:
            img = l.back
        s_rel = sc / SF
        sh = (3 + 14 * hgt) * s_rel, (5 + 22 * hgt) * s_rel, (1.5 + 9 * hgt) * s_rel, 0.38 * hgt
        draw(frame, l, pose_matrix(l, pos, sc, rot, max(abs(sx), 0.03)), shadow=sh, amul=amul, img_override=img)
    pos, sc, rot, hgt = woman_pose(t)
    s_rel = sc / SF
    wp = woman_pyr(t)
    draw(frame, LAYERS['woman'], pose_matrix(LAYERS['woman'], pos, sc, rot),
         shadow=((6 + 16 * hgt) * s_rel, (8 + 26 * hgt) * s_rel, (3 + 14 * hgt) * s_rel, 0.40 * hgt),
         amul=amul, img_override=wp)
    pos, sc, rot, flap, hgt = butterfly_pose(t)
    s_rel = sc / SF
    l = LAYERS['butterfly']
    draw(frame, l, pose_matrix(l, pos, sc, rot, flap, beta=-30),
         shadow=((3 + 18 * hgt) * s_rel, (5 + 26 * hgt) * s_rel, (1.5 + 8 * hgt) * s_rel, 0.36 * hgt), amul=amul)
    draw_burst(frame, t)
    return frame

# ring shards + paper crumbs at the moment of breaking
def make_burst():
    rng = np.random.default_rng(21)
    shards = []
    cuts = np.sort(rng.uniform(0, 2 * np.pi, 17))
    for a0, a1 in zip(cuts, np.roll(cuts, -1)):
        if a1 < a0: a1 += 2 * np.pi
        shards.append(dict(a0=a0, a1=a1, v=rng.uniform(380, 900), spin=rng.uniform(-500, 500),
                           grow=rng.uniform(2.0, 4.5)))
    C = cv2.imread('collage.png')
    crumbs = []
    for _ in range(90):
        ang = rng.uniform(0, 2 * np.pi)
        if rng.random() < 0.5:
            ang = PHI_P + rng.normal(0, 0.9)
        px, py = CC + rng.uniform(0, RC * 0.95) * np.array([math.cos(ang), math.sin(ang)])
        col = C[int(np.clip(py, 0, 1535)), int(np.clip(px, 0, 1023))].astype(np.float32) / 255
        if rng.random() < 0.35: col = CREAM.copy()
        crumbs.append(dict(ang=ang, v=rng.uniform(250, 1300), size=rng.uniform(2.5, 9), col=col,
                           spin=rng.uniform(-900, 900), rot0=rng.uniform(0, 360), g=rng.uniform(150, 600),
                           shape=rng.uniform(0.5, 1.0, 4), life=rng.uniform(0.9, 2.2)))
    return shards, crumbs
SHARDS, CRUMBS = make_burst()

def draw_burst(frame, t):
    dt = t - 14.0
    if dt < 0 or dt > 2.4: return
    over = np.zeros((H, W, 3), np.float32); alpha = np.zeros((H, W), np.float32)
    # shockwave ring
    if dt < 0.3:
        r = R + 900 * ease_out(dt / 0.3, 2)
        cv2.circle(alpha, tuple(np.round(IC * 8).astype(int)), int(r * 8), 0.5 * (1 - dt / 0.3), 3, cv2.LINE_AA, 3)
        over[alpha > 0] = CREAM
    for s in SHARDS:
        if dt > 0.9: break
        fade = 1 - smooth((dt - 0.35) / 0.55)
        am = (s['a0'] + s['a1']) / 2
        dirv = np.array([math.cos(am), math.sin(am)])
        dist = s['v'] * dt * (1 - 0.3 * dt)
        g = 1 + (s['grow'] - 1) * ease_out(dt / 0.6, 2)
        c = IC + dirv * (R + dist)
        ang = np.linspace(s['a0'], s['a1'], 8)
        outer = np.stack([np.cos(ang), np.sin(ang)], 1) * (R + 1.2)
        inner = (np.stack([np.cos(ang), np.sin(ang)], 1) * (R - 2.6))[::-1]
        poly = np.vstack([outer, inner]) - dirv * R
        rr = math.radians(s['spin'] * dt)
        Rm = np.array([[math.cos(rr), -math.sin(rr)], [math.sin(rr), math.cos(rr)]])
        poly = (poly @ Rm.T) * g + c
        P = np.round(poly * 8).astype(np.int32)
        cv2.fillPoly(over, [P], CREAM.tolist(), cv2.LINE_AA, shift=3)
        cv2.fillPoly(alpha, [P], float(fade), cv2.LINE_AA, shift=3)
        cv2.polylines(over, [P], True, (0.55, 0.6, 0.64), 1, cv2.LINE_AA, shift=3)
    for c in CRUMBS:
        if dt > c['life']: continue
        fade = 1 - smooth((dt - c['life'] * 0.6) / (c['life'] * 0.4))
        dirv = np.array([math.cos(c['ang']), math.sin(c['ang'])])
        dist = c['v'] * (1 - math.exp(-dt / 0.45)) * 0.45
        p = IC + dirv * (R * 0.6 + dist) + np.array([0, c['g'] * dt * dt * 0.5])
        sz = c['size'] * (1 + 1.5 * ease_out(dt / 0.8))
        rr = math.radians(c['rot0'] + c['spin'] * dt)
        base = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]]) * c['shape'][:, None]
        Rm = np.array([[math.cos(rr), -math.sin(rr)], [math.sin(rr), math.cos(rr)]])
        poly = (base @ Rm.T) * sz + p
        P = np.round(poly * 8).astype(np.int32)
        cv2.fillPoly(over, [P], c['col'].tolist(), cv2.LINE_AA, shift=3)
        cv2.fillPoly(alpha, [P], float(fade), cv2.LINE_AA, shift=3)
    a = alpha[..., None]
    frame *= 1 - a
    frame += over * a

# ---------------------------------------------------------------- frame assembly
SHUTTER = 0.4 / FPS
def render_time(t, fi):
    return render_pre(t, fi) if t < 14.0 else render_post(t, fi)

def render_frame(fi):
    t = fi / FPS
    if 14.0 + SHUTTER / 2 <= t < 17.5:     # motion blur during the burst
        n = 4
        acc = sum(render_time(t + (i / (n - 1) - 0.5) * SHUTTER, fi) for i in range(n)) / n
    else:
        acc = render_time(t, fi)
    # camera shake on impact
    if 14.0 <= t < 14.7:
        amp = 7 * math.exp(-(t - 14.0) / 0.14)
        r = np.random.default_rng(1000 + fi).uniform(-amp, amp, 2)
        acc = cv2.warpAffine(acc, np.float32([[1, 0, r[0]], [0, 1, r[1]]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    # gentle grain, stronger once the collage is out
    gs = (0.6 + 1.8 * smooth((t - 14.0) / 1.0)) / 255
    rng = np.random.default_rng(fi)
    gn = rng.standard_normal((H // 2, W // 2), dtype=np.float32)
    gn = cv2.resize(gn, (W, H), interpolation=cv2.INTER_LINEAR) * 0.7 + rng.standard_normal((H, W), dtype=np.float32) * 0.5
    acc = acc + (gn * gs)[..., None]
    return (np.clip(acc, 0, 1) * 255 + 0.5).astype(np.uint8)

def main():
    mode = sys.argv[1]
    if mode == 'stills':
        os.makedirs('stills', exist_ok=True)
        for a in sys.argv[2:]:
            fi = int(round(float(a) * FPS))
            cv2.imwrite(f'stills/f{fi:03d}.png', render_frame(fi))
            print('wrote', fi)
        return
    out = sys.argv[2]
    from multiprocessing import Pool
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow',
                           '-crf', '15', '-pix_fmt', 'yuv420p', '-r', str(FPS), out], stdin=subprocess.PIPE)
    frames = range(int(sys.argv[3]) if len(sys.argv) > 3 else 0, NFR)
    with Pool(4) as pool:
        for i, fr in enumerate(pool.imap(render_frame, frames, chunksize=2)):
            ff.stdin.write(fr.tobytes())
            if i % 24 == 0:
                print('frame', i, flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == '__main__':
    main()
