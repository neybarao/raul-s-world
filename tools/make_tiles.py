"""Gera tiles, inimigo, coracoes e camadas de fundo em pixel art simples.

Uso: python3 tools/make_tiles.py
Tudo aqui e placeholder, desenhado por codigo, para substituir pela arte final.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public/assets"
T = 16

GRASS_HI = (120, 214, 64)
GRASS = (76, 178, 48)
GRASS_DK = (38, 120, 40)
DIRT_HI = (196, 112, 58)
DIRT = (160, 82, 42)
DIRT_DK = (112, 54, 30)
OUTLINE = (40, 26, 20)
STONE = (150, 140, 150)
STONE_DK = (100, 92, 108)


def dirt_fill(d, x0, y0, rnd):
    d.rectangle([x0, y0, x0 + T - 1, y0 + T - 1], fill=DIRT)
    for _ in range(9):
        x, y = rnd.randrange(T - 2), rnd.randrange(T - 2)
        d.rectangle([x0 + x, y0 + y, x0 + x + 1, y0 + y], fill=rnd.choice([DIRT_DK, DIRT_HI]))


def grass_top(d, x0, y0, rnd):
    dirt_fill(d, x0, y0, rnd)
    d.rectangle([x0, y0, x0 + T - 1, y0 + 4], fill=GRASS)
    d.line([x0, y0, x0 + T - 1, y0], fill=GRASS_HI)
    # franja irregular do gramado
    for x in range(T):
        h = 5 + (1 if (x * 7) % 5 < 2 else 0) + (1 if x % 4 == 1 else 0)
        d.line([x0 + x, y0 + 4, x0 + x, y0 + h], fill=GRASS if x % 3 else GRASS_DK)
        d.point((x0 + x, y0 + h + 1), fill=GRASS_DK)


def make_tiles():
    rnd = random.Random(7)
    # 0 grama  1 terra  2 grama borda esq  3 grama borda dir  4 terra borda esq  5 terra borda dir
    # 6 plataforma esq  7 plataforma meio  8 plataforma dir
    img = Image.new("RGBA", (T * 9, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    grass_top(d, 0, 0, rnd)
    dirt_fill(d, T, 0, rnd)
    grass_top(d, T * 2, 0, rnd)
    d.line([T * 2, 0, T * 2, T - 1], fill=OUTLINE)
    grass_top(d, T * 3, 0, rnd)
    d.line([T * 4 - 1, 0, T * 4 - 1, T - 1], fill=OUTLINE)
    dirt_fill(d, T * 4, 0, rnd)
    d.line([T * 4, 0, T * 4, T - 1], fill=OUTLINE)
    dirt_fill(d, T * 5, 0, rnd)
    d.line([T * 6 - 1, 0, T * 6 - 1, T - 1], fill=OUTLINE)
    # plataformas flutuantes de pedra com grama
    for i in range(3):
        x0 = T * (6 + i)
        d.rectangle([x0, 4, x0 + T - 1, 11], fill=STONE)
        d.line([x0, 11, x0 + T - 1, 11], fill=STONE_DK)
        d.line([x0, 12, x0 + T - 1, 12], fill=OUTLINE)
        for k in range(0, T, 5):
            d.line([x0 + k + 2, 7, x0 + k + 2, 10], fill=STONE_DK)
        d.rectangle([x0, 0, x0 + T - 1, 3], fill=GRASS)
        d.line([x0, 0, x0 + T - 1, 0], fill=GRASS_HI)
        for x in range(0, T, 3):
            d.point((x0 + x, 4), fill=GRASS_DK)
    d.line([T * 6, 0, T * 6, 12], fill=OUTLINE)
    d.line([T * 9 - 1, 0, T * 9 - 1, 12], fill=OUTLINE)
    extrude(img, 9).save(OUT / "tiles.png")


def extrude(img, count):
    """Copia a borda de cada tile 1px pra fora (margem 1, espacamento 2)."""
    out = Image.new("RGBA", (count * (T + 2), T + 2), (0, 0, 0, 0))
    for i in range(count):
        tile = img.crop((i * T, 0, i * T + T, T))
        ox = i * (T + 2) + 1
        out.paste(tile, (ox, 1))
        out.paste(tile.crop((0, 0, 1, T)), (ox - 1, 1))
        out.paste(tile.crop((T - 1, 0, T, T)), (ox + T, 1))
        out.paste(tile.crop((0, 0, T, 1)), (ox, 0))
        out.paste(tile.crop((0, T - 1, T, T)), (ox, T + 1))
    return out


def make_enemy():
    """Besouro ranzinza: 2 quadros andando + 1 amassado (16x14 cada)."""
    W, H = 16, 14
    img = Image.new("RGBA", (W * 3, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    shell, shell_hi, belly = (122, 62, 168), (176, 112, 220), (60, 30, 80)
    for f in range(2):
        x0 = f * W
        d.ellipse([x0 + 1, 2, x0 + 14, 12], fill=shell, outline=OUTLINE)
        d.line([x0 + 4, 4, x0 + 7, 3], fill=shell_hi)
        d.line([x0 + 8, 3, x0 + 8, 11], fill=OUTLINE)
        # olhos bravos
        d.rectangle([x0 + 2, 6, x0 + 4, 8], fill=(255, 255, 255))
        d.point((x0 + 3, 7), fill=OUTLINE)
        d.line([x0 + 2, 5, x0 + 5, 6], fill=OUTLINE)
        # perninhas
        off = f * 2
        for lx in (3 + off, 7, 11 - off):
            d.line([x0 + lx, 12, x0 + lx, 13], fill=OUTLINE)
        d.line([x0 + 1, 1, x0 + 3, 3], fill=OUTLINE)
    x0 = W * 2
    d.ellipse([x0 + 1, 9, x0 + 14, 13], fill=shell, outline=OUTLINE)
    d.line([x0 + 4, 11, x0 + 6, 11], fill=belly)
    img.save(OUT / "enemy.png")


def make_hearts():
    img = Image.new("RGBA", (18, 8), (0, 0, 0, 0))
    shape = [
        ".XX.XX..",
        "XHHXRRX.",
        "XHRRRRX.",
        "XRRRRRX.",
        ".XRRRX..",
        "..XRX...",
        "...X....",
    ]
    for f, (fill, hi) in enumerate([((226, 40, 52), (255, 140, 140)), ((70, 60, 70), (110, 100, 110))]):
        for y, row in enumerate(shape):
            for x, ch in enumerate(row):
                c = {"X": OUTLINE, "R": fill, "H": hi}.get(ch)
                if c:
                    img.putpixel((f * 9 + x, y), c + (255,))
    img.save(OUT / "hearts.png")


def make_background():
    rnd = random.Random(3)
    # nuvem
    cloud = Image.new("RGBA", (48, 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(cloud)
    for cx, cy, r in [(12, 12, 7), (22, 8, 8), (33, 11, 7), (40, 14, 5)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    d.rectangle([6, 14, 44, 19], fill=(255, 255, 255))
    d.rectangle([6, 17, 44, 19], fill=(214, 232, 250))
    cloud.save(OUT / "cloud.png")

    # morros distantes (tile horizontal de 256px)
    W, H = 256, 96
    hills = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(hills)
    for cx, r in [(30, 60), (120, 75), (200, 55), (286, 60), (-26, 55)]:
        d.ellipse([cx - r, H - r * 0.9, cx + r, H + r], fill=(118, 190, 214))
    hills.save(OUT / "hills-far.png")

    # floresta proxima
    trees = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(trees)
    x = -10
    while x < W + 10:
        r = rnd.randint(12, 20)
        top = H - rnd.randint(36, 60)
        for xx in (x, x + W, x - W):
            d.ellipse([xx - r, top - r, xx + r, top + r], fill=(56, 150, 84))
            d.ellipse([xx - r + 3, top - r + 2, xx + r - 6, top + r - 8], fill=(80, 176, 96))
            d.rectangle([xx - r, top, xx + r, H], fill=(56, 150, 84))
        x += rnd.randint(16, 26)
    trees.save(OUT / "trees-near.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make_tiles()
    make_enemy()
    make_hearts()
    make_background()
    print("ok")
