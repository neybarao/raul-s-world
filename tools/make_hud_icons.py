"""Icones do HUD em pixel art: botoes de pausa/som, moedinha e numeros do contador.

Uso: npm install && python3 tools/make_hud_icons.py   (precisa do rsvg-convert)
Os icones de pausa e som vem da biblioteca Pixelarticons (MIT, https://pixelarticons.com),
instalada pelo npm. Como ja sao desenhados numa grade de 24x24, o script rasteriza cada SVG
nessa grade exata (pixel por pixel) e monta o botao em volta.

Saidas (public/assets/):
- hud-buttons.png: 3 quadros de 30x30 (0 pausa, 1 som ligado, 2 som desligado)
- hud-counter.png: quadros de 7x9 (0-9, depois "x") e moedinha de 10x10 no ultimo quadro (12x12)
"""
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "node_modules/pixelarticons/svg"
OUT = ROOT / "public/assets"

DARK = (27, 27, 42, 255)
BTN = (43, 45, 72, 235)
BTN_HI = (72, 76, 116, 235)
WHITE = (255, 255, 255, 255)
GOLD = (255, 205, 60, 255)
GOLD_HI = (255, 240, 150, 255)
GOLD_SH = (214, 140, 30, 255)


def rasterize(name):
    """Le o SVG (grade 24x24) e devolve uma mascara 24x24, um valor por pixel."""
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "i.png"
        subprocess.run(["rsvg-convert", "-w", "240", "-h", "240", "-o", str(png), str(ICONS / f"{name}.svg")], check=True)
        a = np.asarray(Image.open(png).convert("RGBA"))[..., 3]
    return a[5::10, 5::10] > 127


def rounded(w, h, r):
    m = np.ones((h, w), bool)
    for y in range(r):
        for x in range(r):
            if (r - x - 0.5) ** 2 + (r - y - 0.5) ** 2 > r * r:
                m[y, x] = m[y, w - 1 - x] = m[h - 1 - y, x] = m[h - 1 - y, w - 1 - x] = False
    return m


def button(icon):
    S = 30
    img = np.zeros((S, S, 4), np.uint8)
    img[rounded(S, S, 5)] = DARK
    inner = np.zeros((S, S), bool)
    inner[1:S - 1, 1:S - 1] = rounded(S - 2, S - 2, 4)
    img[inner] = BTN
    hi = np.zeros((S, S), bool)
    hi[2:4, 4:S - 4] = True
    img[hi & inner] = BTN_HI
    mask = np.zeros((S, S), bool)
    mask[3:27, 3:27] = icon
    shadow = np.zeros_like(mask)
    shadow[1:, :] = mask[:-1, :]
    img[shadow & ~mask] = DARK
    img[mask] = WHITE
    return img


GLYPHS = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "x": ["00000", "00000", "10001", "01010", "00100", "01010", "10001"],
}


def outlined(mask, color):
    h, w = mask.shape
    big = np.zeros((h + 2, w + 2), bool)
    big[1:-1, 1:-1] = mask
    grow = big.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            grow |= np.roll(np.roll(big, dy, 0), dx, 1)
    img = np.zeros((h + 2, w + 2, 4), np.uint8)
    img[grow] = DARK
    img[big] = color
    return img


def coin():
    m = rounded(10, 10, 4)
    img = outlined(m, GOLD)  # 12x12
    inner = np.zeros((12, 12), bool)
    inner[1:11, 1:11] = m
    img[3:9, 8][inner[3:9, 8]] = GOLD_SH
    img[8:10, 3:9] = np.where(inner[8:10, 3:9, None], GOLD_SH, img[8:10, 3:9])
    img[3:7, 3] = GOLD_HI
    img[2, 4:7] = GOLD_HI
    img[4:8, 5:7] = GOLD_SH  # marquinha no meio
    img[4:8, 5] = GOLD_HI
    return img


def main():
    # som ligado: alto-falante cheio do "volume-x-solid" com as ondas do "volume-2"
    mute = rasterize("volume-x-solid")
    on = mute.copy()
    on[:, 14:] = rasterize("volume-2")[:, 14:]
    buttons = [button(rasterize("pause-solid")), button(on), button(mute)]
    Image.fromarray(np.concatenate(buttons, axis=1), "RGBA").save(OUT / "hud-buttons.png")

    keys = list("0123456789x")
    cell = 12
    sheet = np.zeros((cell, cell * (len(keys) + 1), 4), np.uint8)
    for i, k in enumerate(keys):
        g = np.array([[c == "1" for c in row] for row in GLYPHS[k]])
        sheet[0:9, i * cell:i * cell + 7] = outlined(g, WHITE)
    sheet[:, len(keys) * cell:] = coin()
    Image.fromarray(sheet, "RGBA").save(OUT / "hud-counter.png")
    print("hud-buttons.png e hud-counter.png gerados")


if __name__ == "__main__":
    main()
