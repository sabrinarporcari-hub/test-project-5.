"""Split the reference collage into paper-cutout layers.

Outputs (in ./layers):
  bg.png            blue paper with the collage cluster painted out
  <name>.png        RGBA cutout of each element at collage resolution
  layers.json       name, bbox, z-order, anchor of every element
"""
import json, os
import cv2
import numpy as np
from scipy import ndimage as ndi

C = cv2.imread('collage.png')
H, W = C.shape[:2]
Bf, Gf, Rf = [C[..., i].astype(int) for i in range(3)]
blue = ((Bf - Rf) > 18) & ((Gf - Rf) > 10)
blue = cv2.morphologyEx(blue.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
nonblue = ~blue
# remove thin doodles (dashed line, star / eye drawings) from the foreground
nb = cv2.morphologyEx(nonblue.astype(np.uint8), cv2.MORPH_OPEN,
                      cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
nb = ndi.binary_fill_holes(nb)

# element polygons, bottom -> top
P = [
    ('burj',      [(450,240),(470,75),(530,85),(585,95),(590,25),(602,25),(607,105),(660,130),(705,200),(705,300),(665,335),(655,405),(500,440),(468,405),(455,330)]),
    ('postcard',  [(735,240),(800,240),(890,300),(885,480),(740,470),(735,300)]),
    ('eiffel',    [(270,262),(428,220),(498,433),(334,472)]),
    ('airplane',  [(45,288),(88,200),(235,212),(352,198),(362,214),(332,248),(250,278),(215,300),(110,304),(78,316)]),
    ('star_top',  [(348,92),(455,92),(455,205),(348,205)]),
    ('leaves',    [(200,340),(272,336),(335,398),(340,445),(272,486),(200,476)]),
    ('heart',     [(82,345),(208,345),(208,468),(82,440)]),
    ('headphones',[(632,195),(800,190),(905,228),(950,300),(955,420),(925,525),(830,525),(790,480),(700,470),(632,425)]),
    ('palm',      [(878,425),(1005,425),(1005,525),(945,535),(905,625),(872,615)]),
    ('orange',    [(508,390),(662,385),(668,500),(560,522),(508,482)]),
    ('vinyl',     None),  # circle, filled below
    ('note_good', [(36,470),(218,452),(272,560),(260,705),(128,705),(46,612)]),
    ('camera',    [(205,425),(512,465),(518,560),(505,645),(238,645),(200,560)]),
    ('bust',      [(498,515),(600,500),(668,535),(672,600),(642,672),(560,694),(502,642)]),
    ('ocean',     [(498,645),(698,645),(698,840),(498,840)]),
    ('books',     [(80,655),(335,655),(378,700),(385,800),(345,895),(80,895)]),
    ('ticket',    [(688,598),(852,566),(875,842),(712,875)]),
    ('hibiscus',  [(818,648),(918,636),(980,720),(945,805),(860,812),(818,762)]),
    ('lily',      [(278,560),(440,555),(532,598),(562,690),(505,795),(400,805),(318,762),(286,700)]),
    ('flowers',   [(298,755),(402,745),(432,800),(405,885),(298,885)]),
    ('butterfly', [(762,728),(832,732),(928,798),(908,855),(800,855),(758,822)]),
    ('star_r',    [(628,785),(745,785),(745,885),(638,895)]),
    ('star_pink', [(76,795),(165,795),(165,890),(76,890)]),
    ('note_same', [(692,858),(910,858),(910,1035),(692,1035)]),
]
woman_poly = [(18,1536),(18,1250),(150,1180),(232,1080),(252,1060),(268,1000),(288,930),(328,868),(378,824),(430,794),(490,778),(552,780),(612,798),(660,828),(700,868),(724,930),(736,1000),(746,1080),(770,1150),(900,1230),(1006,1330),(1006,1536)]

label = np.zeros((H, W), np.int16)  # 0 = none
names = []
for i, (n, poly) in enumerate(P, start=1):
    m = np.zeros((H, W), np.uint8)
    if poly is None:
        cv2.circle(m, (742, 572), 118, 1, -1)
    else:
        cv2.fillPoly(m, [np.array(poly, np.int32)], 1)
    label[(m > 0)] = i
    names.append(n)

wm = np.zeros((H, W), np.uint8)
cv2.fillPoly(wm, [np.array(woman_poly, np.int32)], 1)
WOMAN = len(names) + 1
names.append('woman')
label[wm > 0] = WOMAN

# foreground cluster = non-blue pixels near the cluster (excludes far doodles)
poly_union = label > 0
near = cv2.dilate(poly_union.astype(np.uint8), np.ones((81, 81), np.uint8)) > 0
close = cv2.dilate(poly_union.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
fg = ndi.binary_fill_holes((nb & near) | (nonblue & close))
# pixels in fg not covered by any polygon -> nearest labelled pixel
unl = fg & (label == 0)
_, (iy, ix) = ndi.distance_transform_edt(label == 0, return_indices=True)
label[unl] = label[iy[unl], ix[unl]]
label[~fg] = 0
# woman: above her chin keep only grey photo pixels (drop collage bits caught by the polygon)
WM = label == WOMAN
gray = (np.abs(Bf - Rf) < 22) & (np.abs(Gf - Rf) < 18)
band = np.zeros((H, W), bool); band[:1060] = True
wkeep = WM & (~band | gray)
wkeep = cv2.morphologyEx(wkeep.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
wkeep = cv2.morphologyEx(wkeep, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0
nlab, cc, st, _ = cv2.connectedComponentsWithStats(wkeep.astype(np.uint8))
wkeep = cc == (1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))
wkeep = ndi.binary_fill_holes(wkeep) & WM
drop = WM & ~wkeep
label[drop] = 0
_, (iy, ix) = ndi.distance_transform_edt((label == 0) | (label == WOMAN), return_indices=True)
label[drop] = label[iy[drop], ix[drop]]
label[wkeep] = WOMAN
still0 = drop & (label == 0)

# butterfly: keep only wing/body pixels so it can fly and flap on its own
BF = names.index('butterfly') + 1
HIB = names.index('hibiscus') + 1
Vv = C.max(2).astype(int)
like = ((Bf > Rf + 8) & (Bf > 70)) | (Vv < 75)
bm = (label == BF) & like
bm = cv2.morphologyEx(bm.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
bm = ndi.binary_fill_holes(bm)
nlab, cc, st, _ = cv2.connectedComponentsWithStats(bm.astype(np.uint8))
bm = cc == (1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))
rest = (label == BF) & ~bm
label[rest] = 0
_, (iy, ix) = ndi.distance_transform_edt((label == 0) | (label == BF), return_indices=True)
label[rest] = label[iy[rest], ix[rest]]
label[bm] = BF
# paper that sat under the butterfly: inpaint it and hand it to the hibiscus piece
under = cv2.dilate(bm.astype(np.uint8), np.ones((5, 5), np.uint8))
cream = np.median(C[900:1000, 720:880].reshape(-1, 3), 0).astype(np.float32)
grain = cv2.GaussianBlur(np.random.default_rng(1).normal(0, 6, (H, W)).astype(np.float32), (0, 0), 1.2)
shade = cv2.GaussianBlur(np.random.default_rng(2).normal(0, 1, (H // 16, W // 16)).astype(np.float32), (0, 0), 2)
shade = cv2.resize(shade, (W, H)) * 25
Cu = C.copy()
fill = np.clip(cream[None, None] + (grain + shade)[..., None], 0, 255).astype(np.uint8)
Cu[under > 0] = fill[under > 0]

fg_soft = cv2.GaussianBlur((label > 0).astype(np.float32), (5, 5), 1.0)

os.makedirs('layers', exist_ok=True)
meta = []
for i, n in enumerate(names, start=1):
    m = (label == i).astype(np.uint8)
    nlab, cc, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for k in range(1, nlab):
        if st[k, cv2.CC_STAT_AREA] > 150:
            keep[cc == k] = 1
    m = keep
    if m.sum() == 0:
        print('empty', n); continue
    src = C
    if i == HIB:
        m = m | (under > 0)
        src = Cu
    # extend 2px into neighbouring pieces so reassembled pieces leave no seams
    ext = cv2.dilate(m, np.ones((5, 5), np.uint8)) & (label > 0)
    if i == BF:
        ext = m
        a = cv2.GaussianBlur(m.astype(np.float32), (3, 3), 0.8)
    else:
        a = ext.astype(np.float32) * fg_soft
        a = np.maximum(a, m * fg_soft)
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    pad = 6
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(W, x1 + pad), min(H, y1 + pad)
    rgba = np.dstack([src[y0:y1, x0:x1], (np.clip(a[y0:y1, x0:x1], 0, 1) * 255).astype(np.uint8)])
    cv2.imwrite(f'layers/{n}.png', rgba)
    meta.append(dict(name=n, z=i, bbox=[int(x0), int(y0), int(x1), int(y1)],
                     center=[float(xs.mean()), float(ys.mean())], area=int(m.sum())))
    print(n, x0, y0, x1, y1, m.sum())

# background: paint out the cluster with blue paper
hole = cv2.dilate((label > 0).astype(np.uint8), np.ones((9, 9), np.uint8))
keep = (1 - hole).astype(np.float32)
Cf = C.astype(np.float32)
def pushpull(img, w):
    h0, w0 = w.shape
    if min(h0, w0) <= 4:
        m = (img * w[..., None]).sum((0, 1)) / max(w.sum(), 1e-6)
        return np.broadcast_to(m, img.shape).copy()
    sw = cv2.resize(w, (w0 // 2, h0 // 2), interpolation=cv2.INTER_AREA)
    si = cv2.resize(img * w[..., None], (w0 // 2, h0 // 2), interpolation=cv2.INTER_AREA) / (sw[..., None] + 1e-6)
    coarse = cv2.resize(pushpull(si, np.clip(sw * 4, 0, 1)), (w0, h0), interpolation=cv2.INTER_LINEAR)
    return img * w[..., None] + coarse * (1 - w[..., None])
inp = cv2.GaussianBlur(pushpull(Cf, keep), (0, 0), 25)
# synthetic paper grain matched to the real paper's fine detail
clean = C[20:180, 760:1000].astype(np.float32)
sd = (clean - cv2.GaussianBlur(clean, (0, 0), 8)).std()
rng = np.random.default_rng(7)
def octave(s):
    n = rng.normal(0, 1, (H // s + 2, W // s + 2)).astype(np.float32)
    return cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
g = octave(1) * 0.5 + octave(3) * 0.8 + octave(12) * 0.9 + octave(48) * 1.2
g = g / g.std() * sd
tile = np.dstack([g * 1.0, g * 1.05, g * 1.2])
holef = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 3)[..., None]
bg = C.astype(np.float32) * (1 - holef) + (inp + tile) * holef
cv2.imwrite('layers/bg.png', np.clip(bg, 0, 255).astype(np.uint8))
json.dump(meta, open('layers/layers.json', 'w'), indent=1)

# preview: colored label map
rng = np.random.default_rng(3)
cols = rng.integers(40, 255, (len(names) + 1, 3)); cols[0] = 0
prev = (C * 0.45 + cols[label] * 0.55).astype(np.uint8)
cv2.imwrite('label_preview.png', prev)
