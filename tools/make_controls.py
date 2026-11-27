"""Controles de toque em pixel art, no estilo de um portatil antigo (bege, cruz escura, A e B magenta).

Uso: python3 tools/make_controls.py
Cores tiradas da referencia art/concept/controls-reference.jpg.
Tudo e desenhado pixel por pixel numa grade pequena; o jogo amplia em escala inteira,
entao cada pixel fica nitido em qualquer tela.

Saidas (public/assets/):
- controls.png + controls.json (atlas do Phaser) com os quadros:
  dpad, dpad-left, dpad-right, dpad-up, dpad-down  (44x44, centro da cruz em 20.5, 20.5)
  btn-ring, btn-ring-down  (32x32, botao com o rebaixo bege em volta, para o console em pe)
  btn, btn-down            (32x32, botao solto, para jogar deitado por cima do cenario)
  start, start-down        (32x14)
  lbl-a, lbl-b             (8x8, letras azul-marinho)
  grille                   (22x14, grade do alto-falante)
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public/assets"


def rgba(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


SHADOW = (40, 26, 20, 80)
# cruz
PAD_OUT = rgba("1a1b26")
PAD = rgba("323443")
PAD_HI = rgba("484a5c")
PAD_LO = rgba("25273a")
PAD_DOWN = rgba("26283a")
PAD_HOLE = rgba("202332")
PAD_HOLE_RIM = rgba("3e4054")
ARROW = rgba("a3a3a8")
ARROW_HI = rgba("cfcfd3")
ARROW_DIM = rgba("7c7c84")
# botoes
BTN_OUT = rgba("561333")
BTN = rgba("a82e61")
BTN_HI = rgba("c6487d")
BTN_LO = rgba("86214c")
BTN_SPOT = rgba("e88cb1")
BTN_DOWN = rgba("942653")
RING = rgba("bdaea1")
RING_DARK = rgba("8f8077")
RING_LIGHT = rgba("ddd1c5")
# START
ST_OUT = rgba("3a3236")
ST = rgba("c9c2ba")
ST_HI = rgba("e2dcd5")
ST_LO = rgba("a8a19a")
ST_DOWN = rgba("aaa39c")
NAVY = rgba("2a3566")
# alto-falante
SLOT = rgba("8a7f78")
SLOT_LIGHT = rgba("e0d4c8")


def edges(mask):
    """Pixels da mascara com vizinho de fora em cima/esquerda/baixo/direita."""
    p = np.pad(mask, 1)
    up = mask & ~p[:-2, 1:-1]
    down = mask & ~p[2:, 1:-1]
    left = mask & ~p[1:-1, :-2]
    right = mask & ~p[1:-1, 2:]
    return up, down, left, right


def outline_of(mask):
    p = np.pad(mask, 1)
    grown = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | mask
    return grown & ~mask


def shift(mask, dx, dy):
    out = np.zeros_like(mask)
    h, w = mask.shape
    out[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)] = mask[max(-dy, 0):h - max(dy, 0), max(-dx, 0):w - max(dx, 0)]
    return out


def rounded_rect(w, h, x0, y0, x1, y1, r, W, H):
    """Mascara W x H com um retangulo de cantos arredondados (inclusive x0..x1, y0..y1)."""
    m = np.zeros((H, W), bool)
    m[y0:y1 + 1, x0:x1 + 1] = True
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        for dy in range(r):
            for dx in range(r):
                if (r - dx - 0.5) ** 2 + (r - dy - 0.5) ** 2 > r * r:
                    m[cy + sy * dy, cx + sx * dx] = False
    return m


def circle(W, H, cx, cy, r):
    yy, xx = np.mgrid[0:H, 0:W]
    return (xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2 <= r * r


def paint(img, mask, color):
    img[mask] = color


# ---------- direcional em cruz ----------

def dpad(pressed=None):
    S = 44
    img = np.zeros((S, S, 4), np.uint8)
    lo, hi, arm = 1, 39, 15  # cruz de 1 a 39 (41 px), bracos de 15 px
    a0 = 13
    a1 = a0 + arm - 1
    horiz = rounded_rect(S, S, lo, a0, hi, a1, 3, S, S)
    vert = rounded_rect(S, S, a0, lo, a1, hi, 3, S, S)
    cross = horiz | vert
    out = outline_of(cross)
    body = cross
    full = body | out
    paint(img, shift(full, 2, 2) & ~full, SHADOW)
    paint(img, out, PAD_OUT)
    paint(img, body, PAD)
    up, down, left, right = edges(body)
    paint(img, up | left, PAD_HI)
    down2 = down | (shift(down, 0, -1) & body)
    paint(img, down2 | right, PAD_LO)

    regions = {
        "left": body & (np.mgrid[0:S, 0:S][1] < a0),
        "right": body & (np.mgrid[0:S, 0:S][1] > a1),
        "up": body & (np.mgrid[0:S, 0:S][0] < a0),
        "down": body & (np.mgrid[0:S, 0:S][0] > a1),
    }
    if pressed:
        r = regions[pressed]
        paint(img, r, PAD_DOWN)
        u2, d2, l2, r2 = edges(body)
        paint(img, r & (u2 | l2), PAD_OUT)  # sombra interna: o braco afundou

    # buraco do meio
    c = 20.5
    hole = circle(S, S, c, c, 4.6)
    paint(img, hole, PAD_HOLE)
    paint(img, hole & ~shift(hole, -1, -1), PAD_HOLE_RIM)

    # setas
    def arrow(direction):
        m = np.zeros((S, S), bool)
        t = 7  # distancia da ponta da seta ate a borda do braco
        for i in range(4):  # 4 linhas: 1, 3, 5, 7 pixels
            half = i
            if direction == "up":
                y = lo + t - 3 + i
                m[y, int(c - 0.5) - half:int(c - 0.5) + half + 1] = True
            elif direction == "down":
                y = hi - t + 3 - i
                m[y, int(c - 0.5) - half:int(c - 0.5) + half + 1] = True
            elif direction == "left":
                x = lo + t - 3 + i
                m[int(c - 0.5) - half:int(c - 0.5) + half + 1, x] = True
            else:
                x = hi - t + 3 - i
                m[int(c - 0.5) - half:int(c - 0.5) + half + 1, x] = True
        return m

    for d in ("up", "down", "left", "right"):
        m = arrow(d)
        dim = pressed == d
        paint(img, m, ARROW_DIM if dim else ARROW)
        if not dim:
            u, _, l, _ = edges(m)
            paint(img, m & (u | l), ARROW_HI)
    return img


# ---------- botoes A e B ----------

def button(ring, pressed):
    S = 32
    img = np.zeros((S, S, 4), np.uint8)
    c = 16.0
    yy, xx = np.mgrid[0:S, 0:S]
    upper_left = (xx + yy) < 2 * c - 1
    if ring:
        # rebaixo bege em volta: borda externa escura em cima/esquerda e clara embaixo/direita
        rim = circle(S, S, c, c, 15.5)
        edge = rim & ~circle(S, S, c, c, 14.5)
        paint(img, rim, RING)
        paint(img, edge & upper_left, RING_DARK)
        paint(img, edge & ~upper_left, RING_LIGHT)
    btn0 = circle(S, S, c, c, 11.5)
    btn = shift(btn0, 0, 1) if pressed else btn0
    out_m = outline_of(btn)
    if ring:
        if not pressed:
            paint(img, shift(btn | out_m, 1, 1) & ~(btn | out_m), rgba("a09184"))
    else:
        paint(img, shift(btn | out_m, 2, 2) & ~(btn | out_m), SHADOW)
    paint(img, out_m, BTN_OUT)
    paint(img, btn, BTN_DOWN if pressed else BTN)
    # luz de cima/esquerda e sombra embaixo/direita
    lo_m = btn & ~shift(btn, -2, -2)
    paint(img, lo_m, BTN_OUT if pressed else BTN_LO)
    if not pressed:
        hi_m = btn & ~shift(btn, 2, 2)
        paint(img, hi_m & ~lo_m, BTN_HI)
        spot = circle(S, S, c - 4.5, c - 4.5, 2.3)
        paint(img, spot & btn, BTN_SPOT)
    return img


# ---------- letras ----------

GLYPHS_BIG = {  # 7x7, traco grosso como na referencia
    "A": [
        "..###..",
        ".##.##.",
        "##...##",
        "##...##",
        "#######",
        "##...##",
        "##...##",
    ],
    "B": [
        "######.",
        "##...##",
        "##...##",
        "######.",
        "##...##",
        "##...##",
        "######.",
    ],
}
GLYPHS_SMALL = {  # 3x5
    "S": ["###", "#..", "###", "..#", "###"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
}


def label(ch):
    img = np.zeros((8, 8, 4), np.uint8)
    for y, row in enumerate(GLYPHS_BIG[ch]):
        for x, v in enumerate(row):
            if v == "#":
                img[y, x] = NAVY
    return img


def start(pressed):
    W, H = 32, 14
    img = np.zeros((H, W, 4), np.uint8)
    pill = rounded_rect(W, H, 3, 2, 28, 10, 4, W, H)
    out = outline_of(pill)
    paint(img, shift(pill | out, 0, 1) & ~(pill | out), SHADOW)
    paint(img, out, ST_OUT)
    paint(img, pill, ST_DOWN if pressed else ST)
    up, down, _, _ = edges(pill)
    paint(img, up, ST_LO if pressed else ST_HI)
    if not pressed:
        paint(img, down, ST_LO)
    x = 6 + (1 if pressed else 0)
    y = 4 + (1 if pressed else 0)
    for ch in "START":
        for gy, row in enumerate(GLYPHS_SMALL[ch]):
            for gx, v in enumerate(row):
                if v == "#":
                    img[y + gy, x + gx] = NAVY
        x += 4
    return img


def grille():
    W, H = 22, 14
    img = np.zeros((H, W, 4), np.uint8)
    for i in range(5):
        x = 1 + i * 4
        img[1:13, x:x + 2] = SLOT
        img[1, x:x + 2] = rgba("766c66")
        img[2:13, x + 2] = SLOT_LIGHT
        img[13, x:x + 3] = SLOT_LIGHT
    return img


def main():
    frames = {
        "dpad": dpad(),
        "dpad-left": dpad("left"),
        "dpad-right": dpad("right"),
        "dpad-up": dpad("up"),
        "dpad-down": dpad("down"),
        "btn-ring": button(True, False),
        "btn-ring-down": button(True, True),
        "btn": button(False, False),
        "btn-down": button(False, True),
        "start": start(False),
        "start-down": start(True),
        "lbl-a": label("A"),
        "lbl-b": label("B"),
        "grille": grille(),
    }
    # empilha numa folha simples, uma linha por quadro, com 1 px de folga
    W = max(f.shape[1] for f in frames.values())
    H = sum(f.shape[0] + 1 for f in frames.values())
    sheet = np.zeros((H, W, 4), np.uint8)
    meta = {}
    y = 0
    for name, f in frames.items():
        h, w = f.shape[:2]
        sheet[y:y + h, 0:w] = f
        meta[name] = {
            "frame": {"x": 0, "y": y, "w": w, "h": h},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h},
            "sourceSize": {"w": w, "h": h},
        }
        y += h + 1
    Image.fromarray(sheet, "RGBA").save(OUT / "controls.png")
    (OUT / "controls.json").write_text(json.dumps({"frames": meta, "meta": {"image": "controls.png", "scale": "1"}}, indent=1))
    print("controls.png", sheet.shape[1], "x", sheet.shape[0])


if __name__ == "__main__":
    main()
