"""Retrato do Raul no HUD: 5 expressoes dentro da moldura arredondada.

Uso: python3 tools/make_faces.py
Entrada: art/concept/expressions-sheet.jpg (5 rostos gerados no inicio do projeto, fundo creme).
Saida: public/assets/sprites/raul-faces.png, folha com 5 quadros de 56x56 ja com a moldura
(contorno escuro, borda branca e fundo claro, cantos arredondados em degraus de pixel).
Tudo no mesmo tamanho de pixel, para ampliar em escala inteira no jogo e ficar nitido.

Ordem dos quadros: 0 feliz, 1 rindo, 2 surpreso, 3 piscando, 4 triste.
"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art/concept/expressions-sheet.jpg"
OUT = ROOT / "public/assets/sprites/raul-faces.png"

FACE = 48          # area do rosto, em pixels da arte
BORDER = 4         # 1 contorno + 2 branco + 1 sombra clara
SIZE = FACE + 2 * BORDER
RADIUS = 6
COLORS = 40
BG = np.array([249, 243, 231])
SEGS = [(38, 205), (234, 400), (423, 589), (622, 788), (815, 983)]  # colunas de cada rosto
CROP = 184

OUTLINE = (27, 27, 42, 255)
WHITE = (255, 255, 255, 255)
SHADE = (214, 222, 196, 255)
INNER = (236, 241, 214, 255)


def cut_face(a, s, e):
    cx = (s + e) // 2
    crop = a[8:8 + CROP, cx - CROP // 2: cx + CROP // 2]
    h, w, _ = crop.shape
    isbg = np.abs(crop - BG).sum(2) < 60
    mask = np.zeros((h, w), bool)
    q = deque()
    seeds = [(0, x) for x in range(w)] + [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)]
    for y, x in seeds:
        if isbg[y, x] and not mask[y, x]:
            mask[y, x] = True
            q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx] and isbg[ny, nx]:
                mask[ny, nx] = True
                q.append((ny, nx))
    rgba = np.dstack([crop, np.where(mask, 0, 255)]).astype(np.uint8)
    small = np.asarray(Image.fromarray(rgba, "RGBA").resize((FACE, FACE), Image.BOX)).copy()
    small[..., 3] = np.where(small[..., 3] > 110, 255, 0)
    return small


def rounded(size, r):
    """Mascara de retangulo com cantos arredondados em degraus (sem anti-aliasing)."""
    m = np.ones((size, size), bool)
    for y in range(r):
        for x in range(r):
            if (r - x - 0.5) ** 2 + (r - y - 0.5) ** 2 > r * r:
                for yy, xx in ((y, x), (y, size - 1 - x), (size - 1 - y, x), (size - 1 - y, size - 1 - x)):
                    m[yy, xx] = False
    return m


def frame():
    f = np.zeros((SIZE, SIZE, 4), np.uint8)
    layers = [(0, RADIUS, OUTLINE), (1, RADIUS - 1, WHITE), (3, RADIUS - 3, SHADE), (4, RADIUS - 3, INNER)]
    for inset, r, color in layers:
        n = SIZE - 2 * inset
        m = rounded(n, max(r, 1))
        f[inset:inset + n, inset:inset + n][m] = color
    return f


def main():
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
    faces = [cut_face(a, s, e) for s, e in SEGS]
    # paleta unica para as 5 expressoes
    strip = np.concatenate(faces, axis=1)
    pal = Image.fromarray(strip[..., :3]).quantize(colors=COLORS, method=Image.MEDIANCUT, dither=Image.NONE)
    q = np.asarray(pal.convert("RGB"))
    inner_mask = rounded(FACE, RADIUS - 3)
    sheet = np.zeros((SIZE, SIZE * 5, 4), np.uint8)
    for i in range(5):
        f = frame()
        face = q[:, i * FACE:(i + 1) * FACE]
        opaque = (faces[i][..., 3] > 0) & inner_mask
        region = f[BORDER:BORDER + FACE, BORDER:BORDER + FACE]
        region[opaque, :3] = face[opaque]
        region[opaque, 3] = 255
        sheet[:, i * SIZE:(i + 1) * SIZE] = f
    Image.fromarray(sheet, "RGBA").save(OUT)
    print(f"{OUT.relative_to(ROOT)}: 5 quadros de {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
