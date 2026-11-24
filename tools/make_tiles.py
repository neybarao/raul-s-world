"""Gera tiles, inimigo, coracoes e camadas de fundo no estilo 32 bits (blocos de 32 px).

Uso: python3 tools/make_tiles.py
Desenho por codigo, com varios tons por material, para combinar com os sprites do Raul.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public/assets"
T = 32

OUTLINE = (44, 26, 20)
GRASS = [(40, 112, 44), (58, 146, 50), (84, 178, 58), (122, 206, 74), (172, 232, 110)]
DIRT = [(92, 48, 28), (122, 66, 36), (150, 86, 46), (176, 108, 60), (204, 136, 84)]
STONE = [(78, 72, 88), (108, 102, 118), (140, 134, 150), (172, 166, 180), (204, 200, 212)]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dirt_tile(rnd):
    img = Image.new("RGBA", (T, T))
    p = img.load()
    for y in range(T):
        for x in range(T):
            p[x, y] = (DIRT[2] if rnd.random() > 0.15 else DIRT[1]) + (255,)
    d = ImageDraw.Draw(img)
    # pedrinhas com luz em cima e sombra embaixo
    for _ in range(6):
        x, y = rnd.randrange(2, T - 7), rnd.randrange(2, T - 5)
        w, h = rnd.choice([(4, 3), (5, 3), (3, 2), (6, 4)])
        d.ellipse([x, y, x + w, y + h], fill=DIRT[0])
        d.ellipse([x, y, x + w - 1, y + h - 1], fill=DIRT[3])
        d.point((x + 1, y), fill=DIRT[4])
    for _ in range(3):
        x, y = rnd.randrange(0, T - 5), rnd.randrange(0, T)
        d.line([x, y, x + rnd.randint(2, 5), y], fill=DIRT[1])
    return img


def grass_top(rnd):
    img = dirt_tile(rnd)
    d = ImageDraw.Draw(img)
    p = img.load()
    for y in range(10):
        d.line([0, y, T - 1, y], fill=lerp(GRASS[3], GRASS[1], y / 9))
    d.line([0, 0, T - 1, 0], fill=GRASS[4])
    d.line([0, 1, T - 1, 1], fill=GRASS[3])
    # franja irregular caindo sobre a terra, com sombra na ponta
    for x in range(T):
        drop = 10 + int(2 + 2 * math.sin(x * 0.9) + rnd.random() * 2.5)
        for y in range(10, drop):
            p[x, y] = GRASS[1] + (255,)
        p[x, drop] = GRASS[0] + (255,)
        if drop + 1 < T:
            p[x, drop + 1] = DIRT[1] + (255,)
    for _ in range(7):
        x = rnd.randrange(1, T - 2)
        d.line([x, 3, x, 6], fill=GRASS[4])
        d.point((x + 1, 4), fill=GRASS[3])
    return img


def edge(img, side):
    """Borda lateral com contorno e luz/sombra (lado do buraco)."""
    d = ImageDraw.Draw(img)
    x = 0 if side == "l" else T - 1
    inner = 1 if side == "l" else T - 2
    for y in range(T):
        c = img.getpixel((inner, y))[:3]
        d.point((inner, y), fill=lerp(c, (255, 255, 255), 0.25) if side == "l" else lerp(c, (0, 0, 0), 0.3))
    d.line([x, 0, x, T - 1], fill=OUTLINE)
    return img


def platform(part, rnd):
    img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 8, T - 1, 24], fill=STONE[2])
    d.line([0, 9, T - 1, 9], fill=STONE[4])
    d.line([0, 10, T - 1, 10], fill=STONE[3])
    d.line([0, 22, T - 1, 22], fill=STONE[1])
    d.line([0, 23, T - 1, 23], fill=STONE[0])
    d.line([0, 24, T - 1, 24], fill=OUTLINE)
    for k in (6, 18, 28):
        d.line([k, 11, k, 21], fill=STONE[1])
        d.line([k + 1, 11, k + 1, 21], fill=STONE[3])
    for _ in range(4):
        d.point((rnd.randrange(2, T - 3), rnd.randrange(12, 20)), fill=STONE[1])
    for y in range(8):
        d.line([0, y, T - 1, y], fill=lerp(GRASS[3], GRASS[1], y / 7))
    d.line([0, 0, T - 1, 0], fill=GRASS[4])
    for x in range(0, T, 3):
        d.line([x, 8, x, 9 + (x % 2)], fill=GRASS[0])
    for _ in range(4):
        x = rnd.randrange(1, T - 2)
        d.line([x, 2, x, 4], fill=GRASS[4])
    if part == "l":
        d.line([0, 0, 0, 24], fill=OUTLINE)
        d.line([1, 1, 1, 23], fill=lerp(STONE[3], (255, 255, 255), 0.2))
    if part == "r":
        d.line([T - 1, 0, T - 1, 24], fill=OUTLINE)
        d.line([T - 2, 1, T - 2, 23], fill=STONE[0])
    return img


def extrude(tiles):
    """Copia a borda de cada tile 1px para fora (margem 1, espacamento 2)."""
    out = Image.new("RGBA", (len(tiles) * (T + 2), T + 2), (0, 0, 0, 0))
    for i, tile in enumerate(tiles):
        ox = i * (T + 2) + 1
        out.paste(tile, (ox, 1))
        out.paste(tile.crop((0, 0, 1, T)), (ox - 1, 1))
        out.paste(tile.crop((T - 1, 0, T, T)), (ox + T, 1))
        out.paste(tile.crop((0, 0, T, 1)), (ox, 0))
        out.paste(tile.crop((0, T - 1, T, T)), (ox, T + 1))
    return out


def make_tiles():
    rnd = random.Random(7)
    # 0 grama  1 terra  2 grama esq  3 grama dir  4 terra esq  5 terra dir  6-8 plataforma
    tiles = [
        grass_top(rnd), dirt_tile(rnd),
        edge(grass_top(rnd), "l"), edge(grass_top(rnd), "r"),
        edge(dirt_tile(rnd), "l"), edge(dirt_tile(rnd), "r"),
        platform("l", rnd), platform("m", rnd), platform("r", rnd),
    ]
    extrude(tiles).save(OUT / "tiles.png")


def make_enemy():
    """Besouro ranzinza com casco brilhante: 2 quadros andando + 1 amassado (32x28 cada)."""
    W, H = 32, 28
    img = Image.new("RGBA", (W * 3, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    shell = [(62, 26, 92), (98, 44, 140), (132, 66, 184), (176, 112, 222), (226, 190, 250)]
    for f in range(2):
        x0, bob = f * W, f
        for i, lx in enumerate((10, 17, 24)):
            off = 2 if (i + f) % 2 else -2
            d.line([x0 + lx, 20 + bob, x0 + lx + off, 27], fill=OUTLINE, width=2)
        d.ellipse([x0 + 4, 4 + bob, x0 + 31, 24 + bob], fill=OUTLINE)
        d.ellipse([x0 + 6, 6 + bob, x0 + 29, 22 + bob], fill=shell[1])
        d.ellipse([x0 + 7, 6 + bob, x0 + 27, 18 + bob], fill=shell[2])
        d.ellipse([x0 + 11, 7 + bob, x0 + 21, 12 + bob], fill=shell[3])
        d.ellipse([x0 + 13, 8 + bob, x0 + 16, 10 + bob], fill=shell[4])
        d.line([x0 + 18, 6 + bob, x0 + 18, 22 + bob], fill=shell[0], width=2)
        d.ellipse([x0, 11 + bob, x0 + 12, 23 + bob], fill=OUTLINE)
        d.ellipse([x0 + 1, 12 + bob, x0 + 11, 22 + bob], fill=(64, 46, 72))
        d.ellipse([x0 + 2, 14 + bob, x0 + 7, 19 + bob], fill=(255, 255, 255))
        d.rectangle([x0 + 3, 16 + bob, x0 + 4, 17 + bob], fill=OUTLINE)
        d.line([x0 + 1, 13 + bob, x0 + 8, 15 + bob], fill=OUTLINE, width=2)
        d.line([x0 + 5, 11 + bob, x0 + 2, 5 + bob], fill=OUTLINE)
        d.point((x0 + 2, 4 + bob), fill=shell[3])
    x0 = W * 2
    d.ellipse([x0 + 2, 18, x0 + 29, 27], fill=OUTLINE)
    d.ellipse([x0 + 4, 19, x0 + 27, 26], fill=shell[1])
    d.ellipse([x0 + 6, 19, x0 + 20, 23], fill=shell[3])
    img.save(OUT / "enemy.png")


def make_hearts():
    """Coracao cheio e vazio, 18x16, com brilho."""
    img = Image.new("RGBA", (36, 16), (0, 0, 0, 0))
    for f, cols in enumerate([
        [(150, 20, 34), (214, 36, 50), (246, 84, 92), (255, 196, 196)],
        [(48, 40, 52), (76, 66, 82), (100, 90, 108), (140, 130, 150)],
    ]):
        layer = Image.new("RGBA", (18, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.ellipse([0, 0, 9, 9], fill=OUTLINE)
        d.ellipse([8, 0, 17, 9], fill=OUTLINE)
        d.polygon([(0, 5), (17, 5), (9, 15)], fill=OUTLINE)
        d.ellipse([1, 1, 8, 8], fill=cols[1])
        d.ellipse([9, 1, 16, 8], fill=cols[1])
        d.polygon([(1, 5), (16, 5), (9, 13)], fill=cols[1])
        d.polygon([(4, 9), (14, 9), (9, 13)], fill=cols[0])
        d.ellipse([2, 2, 6, 5], fill=cols[2])
        d.rectangle([3, 2, 4, 3], fill=cols[3])
        img.alpha_composite(layer, (f * 18, 0))
    img.save(OUT / "hearts.png")


def make_background():
    rnd = random.Random(3)
    cloud = Image.new("RGBA", (96, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(cloud)
    blobs = [(22, 24, 13), (42, 15, 15), (64, 21, 14), (80, 27, 10)]
    for cx, cy, r in blobs:
        d.ellipse([cx - r, cy - r + 3, cx + r, cy + r + 3], fill=(184, 212, 240))
    d.rectangle([10, 28, 88, 37], fill=(184, 212, 240))
    for cx, cy, r in blobs:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    d.rectangle([10, 24, 88, 33], fill=(255, 255, 255))
    d.rectangle([10, 33, 88, 35], fill=(222, 236, 250))
    cloud.save(OUT / "cloud.png")

    W, H = 512, 192
    hills = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(hills)
    for color, items in (
        ((138, 196, 222), [(70, 130), (250, 150), (420, 120), (-90, 120), (590, 130)]),
        ((112, 178, 206), [(150, 100), (330, 110), (500, 95), (-30, 95)]),
    ):
        for cx, r in items:
            d.ellipse([cx - r, H - r * 0.85, cx + r, H + r], fill=color)
    hills.save(OUT / "hills-far.png")

    trees = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(trees)
    tones = [(36, 112, 64), (50, 140, 76), (72, 166, 90), (110, 196, 112)]
    crowns, x = [], -20
    while x < W + 20:
        crowns.append((x, rnd.randint(24, 40), H - rnd.randint(70, 120)))
        x += rnd.randint(32, 52)
    for shift in (0, W, -W):
        for cx, r, top in crowns:
            xx = cx + shift
            d.rectangle([xx - r, top, xx + r, H], fill=tones[0])
            d.ellipse([xx - r, top - r, xx + r, top + r], fill=tones[1])
            d.ellipse([xx - r + 4, top - r + 3, xx + r - 8, top + r - 10], fill=tones[2])
            d.ellipse([xx - r + 8, top - r + 6, xx - r + 18, top - r + 13], fill=tones[3])
    trees.save(OUT / "trees-near.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make_tiles()
    make_enemy()
    make_hearts()
    make_background()
    print("ok")
