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


# ======================= FASES NOVAS (temas) =======================
# Cada tema gera: tiles-<tema>.png (9 tiles), mola-<tema>.png (2 quadros 32x24)
# e o inimigo da fase. Cores vem das fotos de ferias (paletas extraidas das fotos).

THEMES = {
    "aquario": {
        "top": "moss", "top_cols": [(26, 92, 88), (40, 128, 110), (70, 160, 130), (120, 196, 160), (190, 230, 200)],
        "body": "rock", "body_cols": [(34, 58, 66), (52, 84, 92), (70, 108, 112), (96, 136, 132), (140, 176, 166)],
        "plat": "coral", "plat_cols": [(80, 60, 100), (150, 70, 120), (220, 110, 150), (250, 170, 190), (255, 220, 230)],
    },
    "bolinhas": {
        "top": "foam", "top_cols": [(216, 48, 44), (246, 207, 30), (31, 69, 181), (60, 174, 70), (255, 255, 255)],
        "body": "padding", "body_cols": [(110, 116, 128), (150, 156, 168), (184, 188, 196), (210, 214, 220), (236, 238, 242)],
        "plat": "block", "plat_cols": [(120, 150, 40), (160, 190, 60), (190, 210, 90), (220, 232, 150), (245, 250, 210)],
    },
    "parque": {
        "top": "coping", "top_cols": [(150, 160, 170), (200, 206, 212), (232, 236, 240), (248, 250, 252), (255, 255, 255)],
        "body": "grid", "body_cols": [(40, 110, 150), (70, 160, 200), (120, 200, 228), (170, 226, 242), (230, 248, 255)],
        "plat": "float", "plat_cols": [(150, 40, 80), (220, 90, 130), (240, 140, 170), (250, 200, 215), (255, 255, 255)],
    },
    "quartel": {
        "top": "moss", "top_cols": [(40, 82, 34), (62, 112, 44), (90, 138, 58), (130, 170, 80), (180, 206, 120)],
        "body": "dirt", "body_cols": [(84, 60, 40), (110, 82, 56), (132, 102, 72), (150, 121, 102), (172, 150, 130)],
        "plat": "crate", "plat_cols": [(52, 58, 36), (74, 90, 58), (107, 122, 74), (140, 152, 100), (190, 196, 150)],
    },
    "escolinha": {
        "top": "floor", "top_cols": [(150, 140, 128), (196, 188, 176), (209, 200, 182), (230, 224, 212), (248, 244, 236)],
        "body": "grid", "body_cols": [(150, 130, 112), (190, 170, 150), (207, 186, 169), (225, 207, 190), (240, 228, 214)],
        "plat": "books", "plat_cols": [(213, 104, 39), (76, 160, 90), (60, 110, 200), (230, 190, 40), (246, 154, 82)],
    },
    "praia": {
        "top": "sand", "top_cols": [(190, 172, 130), (214, 198, 160), (232, 222, 192), (244, 238, 216), (255, 252, 240)],
        "body": "speckle", "body_cols": [(150, 126, 90), (178, 152, 110), (200, 178, 136), (220, 202, 164), (236, 224, 196)],
        "plat": "wood", "plat_cols": [(90, 54, 30), (128, 80, 44), (164, 110, 64), (196, 144, 92), (226, 182, 130)],
    },
}


def body_tile(style, C, rnd):
    img = Image.new("RGBA", (T, T), C[2] + (255,))
    d = ImageDraw.Draw(img)
    p = img.load()
    if style == "rock":
        for y in range(T):
            for x in range(T):
                if rnd.random() < 0.18:
                    p[x, y] = C[1] + (255,)
        for _ in range(4):
            x, y, r = rnd.randrange(0, T), rnd.randrange(0, T), rnd.randint(3, 6)
            d.ellipse([x - r, y - r, x + r, y + r], fill=C[1])
            d.ellipse([x - r, y - r, x + r - 2, y + r - 2], fill=C[3])
            d.point((x - r + 2, y - r + 2), fill=C[4])
    elif style == "padding":
        d.rectangle([0, 0, T - 1, T - 1], fill=C[2])
        d.rectangle([1, 1, T - 3, 3], fill=C[3])
        d.line([0, T // 2, T - 1, T // 2], fill=C[1])
        d.line([0, T // 2 + 1, T - 1, T // 2 + 1], fill=C[3])
        d.line([T - 1, 0, T - 1, T - 1], fill=C[0])
        d.line([T // 2, T // 2 + 2, T // 2, T - 1], fill=C[1])
    elif style == "grid":
        s = 8
        for gy in range(0, T, s):
            for gx in range(0, T, s):
                d.rectangle([gx, gy, gx + s - 1, gy + s - 1], fill=C[2])
                d.line([gx + 1, gy + 1, gx + s - 3, gy + 1], fill=C[3])
                d.point((gx + 1, gy + 2), fill=C[3])
                d.line([gx, gy + s - 1, gx + s - 1, gy + s - 1], fill=C[1])
                d.line([gx + s - 1, gy, gx + s - 1, gy + s - 1], fill=C[1])
                if rnd.random() < 0.15:
                    d.point((gx + 3, gy + 3), fill=C[4])
    elif style in ("speckle", "dirt"):
        for y in range(T):
            for x in range(T):
                r = rnd.random()
                if r < 0.12:
                    p[x, y] = C[1] + (255,)
                elif r < 0.22:
                    p[x, y] = C[3] + (255,)
        for _ in range(2 if style == "speckle" else 0):  # conchinhas (so na praia)
            x, y = rnd.randrange(3, T - 5), rnd.randrange(3, T - 4)
            d.ellipse([x, y, x + 4, y + 3], fill=(240, 200, 200))
            d.point((x + 2, y + 1), fill=(200, 140, 140))
    return img


def top_tile(theme, rnd, idx):
    th = THEMES[theme]
    C, style = th["top_cols"], th["top"]
    img = body_tile(th["body"], th["body_cols"], rnd)
    d = ImageDraw.Draw(img)
    p = img.load()
    if style == "moss":
        for y in range(8):
            d.line([0, y, T - 1, y], fill=lerp(C[3], C[1], y / 7))
        d.line([0, 0, T - 1, 0], fill=C[4])
        for x in range(T):
            drop = 8 + int(2 + 2 * math.sin(x * 1.3) + rnd.random() * 2)
            for y in range(8, drop):
                p[x, y] = C[1] + (255,)
            p[x, drop] = C[0] + (255,)
        for _ in range(3):  # pedrinhas claras na areia do fundo
            x = rnd.randrange(2, T - 4)
            d.ellipse([x, 2, x + 3, 4], fill=C[4])
    elif style == "foam":
        col = C[idx % 4]
        hi = lerp(col, (255, 255, 255), 0.45)
        dk = lerp(col, (0, 0, 0), 0.35)
        d.rectangle([0, 0, T - 1, 9], fill=col)
        d.line([0, 0, T - 1, 0], fill=hi)
        d.line([0, 1, T - 1, 1], fill=hi)
        d.line([0, 9, T - 1, 9], fill=dk)
        d.line([0, 10, T - 1, 10], fill=OUTLINE)
        d.point((3, 3), fill=(255, 255, 255))
    elif style == "coping":
        d.rectangle([0, 0, T - 1, 7], fill=C[3])
        d.line([0, 0, T - 1, 0], fill=C[4])
        d.line([0, 6, T - 1, 6], fill=C[1])
        d.line([0, 7, T - 1, 7], fill=C[0])
        for x in (8, 24):
            d.line([x, 1, x, 5], fill=C[2])
        # agua escorrendo
        d.line([0, 8, T - 1, 8], fill=(150, 220, 240))
    elif style == "floor":
        # piso de marmore da escola, com rodape
        d.rectangle([0, 0, T - 1, 8], fill=C[3])
        d.line([0, 0, T - 1, 0], fill=C[4])
        d.line([0, 8, T - 1, 8], fill=C[1])
        d.line([0, 9, T - 1, 9], fill=C[0])
        for x in range(0, T, 16):
            d.line([x, 1, x, 7], fill=C[2])
        for _ in range(3):
            d.line([rnd.randrange(2, T - 6), rnd.randrange(2, 6), rnd.randrange(8, T - 2), rnd.randrange(2, 6)], fill=C[2])
    elif style == "sand":
        for y in range(7):
            d.line([0, y, T - 1, y], fill=lerp(C[4], C[2], y / 6))
        for x in range(T):
            drop = 7 + int(1 + 1.5 * math.sin(x * 0.7) + rnd.random() * 1.5)
            for y in range(7, drop):
                p[x, y] = C[2] + (255,)
            p[x, drop] = C[1] + (255,)
        for _ in range(5):
            d.point((rnd.randrange(0, T), rnd.randrange(1, 6)), fill=C[1])
    return img


def theme_platform(theme, part, rnd):
    th = THEMES[theme]
    C, style = th["plat_cols"], th["plat"]
    img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if style == "wood":
        d.rectangle([0, 4, T - 1, 22], fill=C[2])
        for y in (4, 10, 16):
            d.line([0, y, T - 1, y], fill=C[3])
            d.line([0, y + 5, T - 1, y + 5], fill=C[1])
        d.line([0, 22, T - 1, 22], fill=OUTLINE)
        for x in (4, T - 5):
            d.ellipse([x - 1, 6, x + 1, 8], fill=C[0])
        d.line([0, 4, T - 1, 4], fill=C[4])
    elif style == "coral":
        d.rectangle([0, 6, T - 1, 22], fill=(84, 112, 116))
        d.line([0, 22, T - 1, 22], fill=OUTLINE)
        d.line([0, 6, T - 1, 6], fill=(140, 176, 166))
        for _ in range(5):
            x, y, r = rnd.randrange(2, T - 2), rnd.randrange(2, 9), rnd.randint(2, 4)
            d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.choice(C[1:4]))
            d.point((x - 1, y - 1), fill=C[4])
    elif style == "block":
        d.rectangle([0, 2, T - 1, 22], fill=C[2])
        d.rectangle([0, 2, T - 1, 5], fill=C[3])
        d.line([0, 2, T - 1, 2], fill=C[4])
        d.line([0, 20, T - 1, 20], fill=C[1])
        d.line([0, 22, T - 1, 22], fill=OUTLINE)
        d.line([T // 2, 6, T // 2, 19], fill=C[1])
    elif style == "float":
        d.rounded_rectangle([0, 4, T - 1, 20], radius=6, fill=C[2])
        for x in range(0, T, 16):
            d.rectangle([x + 8, 5, x + 15, 19], fill=C[4])
        d.line([2, 6, T - 3, 6], fill=C[3])
        d.line([2, 19, T - 3, 19], fill=C[0])
        d.line([0, 21, T - 1, 21], fill=OUTLINE)
    elif style == "crate":
        # caixote militar verde-oliva
        d.rectangle([0, 2, T - 1, 22], fill=C[2])
        d.rectangle([0, 2, T - 1, 4], fill=C[3])
        d.line([0, 2, T - 1, 2], fill=C[4])
        d.line([0, 20, T - 1, 20], fill=C[1])
        d.line([0, 22, T - 1, 22], fill=OUTLINE)
        d.line([2, 6, T - 3, 18], fill=C[1])
        d.line([2, 18, T - 3, 6], fill=C[1])
        d.rectangle([T // 2 - 4, 9, T // 2 + 3, 14], fill=C[0])
        d.rectangle([T // 2 - 3, 10, T // 2 + 2, 13], fill=(230, 220, 120))
    elif style == "books":
        # pilha de livros coloridos
        y = 22
        for i, h in enumerate((7, 6, 6)):
            col = C[(i + (1 if part == "m" else 0) + (2 if part == "r" else 0)) % 5]
            x0, x1 = (1 + i, T - 2 - i) if part == "m" else (i % 2, T - 1 - (i + 1) % 2)
            d.rectangle([x0, y - h, x1, y], fill=OUTLINE)
            d.rectangle([x0 + 1, y - h + 1, x1 - 1, y - 1], fill=col)
            d.line([x0 + 1, y - 2, x1 - 1, y - 2], fill=(250, 246, 236))
            d.line([x0 + 1, y - h + 1, x1 - 1, y - h + 1], fill=lerp(col, (255, 255, 255), 0.4))
            y -= h
    if part == "l":
        d.line([0, 2, 0, 22], fill=OUTLINE)
    if part == "r":
        d.line([T - 1, 2, T - 1, 22], fill=OUTLINE)
    return img


def make_theme_tiles(theme):
    rnd = random.Random(hash(theme) % 1000)
    th = THEMES[theme]
    tiles = [
        top_tile(theme, rnd, 0), body_tile(th["body"], th["body_cols"], rnd),
        edge(top_tile(theme, rnd, 1), "l"), edge(top_tile(theme, rnd, 2), "r"),
        edge(body_tile(th["body"], th["body_cols"], rnd), "l"), edge(body_tile(th["body"], th["body_cols"], rnd), "r"),
        theme_platform(theme, "l", rnd), theme_platform(theme, "m", rnd), theme_platform(theme, "r", rnd),
    ]
    extrude(tiles).save(OUT / f"tiles-{theme}.png")


def make_springs():
    """Mola de cada fase (2 quadros 32x24: normal e apertada)."""
    looks = {
        "floresta": ("board", (60, 150, 70), (130, 210, 120)),
        "aquario": ("clam", (130, 80, 160), (200, 150, 230)),
        "bolinhas": ("tramp", (216, 48, 44), (246, 207, 30)),
        "parque": ("ring", (230, 100, 140), (255, 255, 255)),
        "praia": ("ring", (240, 120, 40), (255, 255, 255)),
        "quartel": ("tire", (40, 40, 44), (90, 90, 96)),
        "escolinha": ("tramp", (213, 104, 39), (246, 154, 82)),
    }
    for theme, (kind, c1, c2) in looks.items():
        img = Image.new("RGBA", (64, 24), (0, 0, 0, 0))
        for f in range(2):
            layer = Image.new("RGBA", (32, 24), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            top = 6 if f == 0 else 12
            dark = lerp(c1, (0, 0, 0), 0.4)
            if kind in ("board", "tramp"):
                # pernas / mola
                for x in (6, 24):
                    d.line([x, top + 4, x, 23], fill=OUTLINE, width=2)
                zig = [(10 + (i % 2) * 12, top + 4 + i * ((19 - top) // 4)) for i in range(5)]
                d.line(zig, fill=(160, 160, 170), width=2)
                d.rounded_rectangle([1, top, 30, top + 5], radius=2, fill=OUTLINE)
                d.rounded_rectangle([2, top + 1, 29, top + 4], radius=2, fill=c1)
                d.line([4, top + 1, 27, top + 1], fill=c2)
            elif kind == "clam":
                d.ellipse([2, 12, 29, 23], fill=OUTLINE)
                d.ellipse([3, 13, 28, 22], fill=c1)
                d.ellipse([3, top, 28, top + 12 - (f * 4)], fill=OUTLINE)
                d.ellipse([4, top + 1, 27, top + 11 - (f * 4)], fill=c2)
                d.ellipse([13, 14, 18, 19], fill=(250, 250, 255))
            elif kind == "tire":
                # pneu deitado (achatado quando pisa)
                h = 14 if f == 0 else 9
                y0 = 23 - h
                d.ellipse([1, y0, 30, 23], fill=OUTLINE)
                d.ellipse([2, y0 + 1, 29, 22], fill=c2)
                d.ellipse([3, y0 + 1, 28, 20], fill=c1)
                d.ellipse([9, y0 + h // 3, 22, 23 - h // 3], fill=OUTLINE)
                for x in range(5, 27, 4):
                    d.line([x, y0 + 2, x + 1, y0 + 4], fill=c2)
            elif kind == "ring":
                h = 16 if f == 0 else 10
                y0 = 23 - h
                d.ellipse([1, y0, 30, 23], fill=OUTLINE)
                d.ellipse([2, y0 + 1, 29, 22], fill=c1)
                for x0 in (8, 20):
                    d.rectangle([x0, y0 + 1, x0 + 4, 22], fill=c2)
                d.ellipse([10, y0 + h // 3, 21, 23 - h // 3], fill=OUTLINE)
                d.ellipse([11, y0 + h // 3 + 1, 20, 22 - h // 3], fill=(120, 200, 230))
                d.arc([4, y0 + 2, 27, 21], 200, 300, fill=lerp(c1, (255, 255, 255), 0.5))
            img.alpha_composite(layer, (f * 32, 0))
        img.save(OUT / f"mola-{theme}.png")


def make_theme_enemies():
    """Inimigos das fases novas: 3 quadros 32x32 (andando 1, andando 2, amassado)."""
    W = 32
    # caranguejo (praia)
    img = Image.new("RGBA", (W * 3, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    red, redh, redd = (226, 70, 40), (250, 140, 100), (150, 40, 24)
    for f in range(2):
        x0 = f * W
        for i, lx in enumerate((8, 12, 20, 24)):
            off = 2 if (i + f) % 2 else -2
            d.line([x0 + lx, 22, x0 + lx + off, 30], fill=OUTLINE, width=2)
        d.ellipse([x0 + 4, 12, x0 + 28, 26], fill=OUTLINE)
        d.ellipse([x0 + 5, 13, x0 + 27, 25], fill=red)
        d.ellipse([x0 + 8, 14, x0 + 18, 18], fill=redh)
        d.line([x0 + 6, 24, x0 + 26, 24], fill=redd)
        for cx in (4, 27):  # garras
            up = 2 if f else 0
            d.ellipse([x0 + cx - 4, 6 - up, x0 + cx + 4, 14 - up], fill=OUTLINE)
            d.ellipse([x0 + cx - 3, 7 - up, x0 + cx + 3, 13 - up], fill=red)
            d.line([x0 + cx - 1, 7 - up, x0 + cx + 1, 10 - up], fill=OUTLINE)
        for ex in (12, 20):  # olhos
            d.line([x0 + ex, 13, x0 + ex, 9], fill=OUTLINE, width=2)
            d.ellipse([x0 + ex - 2, 5, x0 + ex + 2, 9], fill=(255, 255, 255), outline=OUTLINE)
            d.point((x0 + ex, 7), fill=OUTLINE)
    x0 = W * 2
    d.ellipse([x0 + 3, 22, x0 + 29, 31], fill=OUTLINE)
    d.ellipse([x0 + 4, 23, x0 + 28, 30], fill=red)
    img.save(OUT / "enemy-caranguejo.png")

    # agua-viva (aquario): flutua, nao anda
    img = Image.new("RGBA", (W * 3, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pink, pinkh, pinkd = (236, 120, 190), (255, 200, 232), (170, 70, 140)
    for f in range(2):
        x0 = f * W
        for i, tx in enumerate((9, 14, 19, 24)):
            wob = 2 if (i + f) % 2 else -2
            d.line([x0 + tx, 16, x0 + tx + wob, 24, x0 + tx, 30], fill=pinkd, width=2)
        squish = f * 2
        d.pieslice([x0 + 3 - squish, 2 + squish, x0 + 29 + squish, 28], 180, 360, fill=OUTLINE)
        d.pieslice([x0 + 4 - squish, 3 + squish, x0 + 28 + squish, 27], 180, 360, fill=pink)
        d.ellipse([x0 + 8, 6 + squish, x0 + 15, 10 + squish], fill=pinkh)
        d.line([x0 + 3, 15, x0 + 29, 15], fill=OUTLINE, width=2)
        d.ellipse([x0 + 11, 9, x0 + 14, 12], fill=OUTLINE)
        d.ellipse([x0 + 18, 9, x0 + 21, 12], fill=OUTLINE)
    x0 = W * 2
    d.ellipse([x0 + 3, 22, x0 + 29, 30], fill=OUTLINE)
    d.ellipse([x0 + 4, 23, x0 + 28, 29], fill=pink)
    img.save(OUT / "enemy-aguaviva.png")

    # bola saltitante (piscina de bolinhas)
    img = Image.new("RGBA", (W * 3, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bc, bh, bd = (31, 69, 181), (120, 150, 240), (16, 36, 110)
    for f, (w, h) in enumerate([(26, 26), (28, 24), (30, 14)]):
        x0 = f * W
        bx, by = x0 + (W - w) // 2, W - h - 1
        d.ellipse([bx, by, bx + w, by + h], fill=OUTLINE)
        d.ellipse([bx + 1, by + 1, bx + w - 1, by + h - 1], fill=bc)
        d.ellipse([bx + 2, by + h * 0.55, bx + w - 2, by + h - 2], fill=bd)
        d.ellipse([bx + 2, by + 1, bx + w - 4, by + h * 0.75], fill=bc)
        d.ellipse([bx + 5, by + 3, bx + 11, by + 3 + h * 0.25], fill=bh)
        if f < 2:  # olhos bravos
            ey = by + h * 0.45
            for ex in (bx + w * 0.38, bx + w * 0.66):
                d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 255, 255))
                d.rectangle([ex - 1, ey - 1, ex, ey + 1], fill=OUTLINE)
            d.line([bx + w * 0.25, ey - 6, bx + w * 0.45, ey - 3], fill=OUTLINE, width=2)
            d.line([bx + w * 0.78, ey - 6, bx + w * 0.58, ey - 3], fill=OUTLINE, width=2)
    img.save(OUT / "enemy-bola.png")

    # patinho de borracha (parque aquatico)
    img = Image.new("RGBA", (W * 3, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    yl, yh, yd, beak = (250, 210, 40), (255, 240, 150), (210, 150, 20), (240, 120, 30)
    for f in range(2):
        x0 = f * W
        bob = f
        d.ellipse([x0 + 3, 14 + bob, x0 + 27, 30], fill=OUTLINE)
        d.ellipse([x0 + 4, 15 + bob, x0 + 26, 29], fill=yl)
        d.ellipse([x0 + 6, 16 + bob, x0 + 16, 21 + bob], fill=yh)
        d.polygon([(x0 + 3, 20 + bob), (x0 + 0, 15 + bob), (x0 + 7, 18 + bob)], fill=yd)  # rabinho
        d.ellipse([x0 + 15, 3 + bob, x0 + 29, 17 + bob], fill=OUTLINE)
        d.ellipse([x0 + 16, 4 + bob, x0 + 28, 16 + bob], fill=yl)
        d.ellipse([x0 + 18, 5 + bob, x0 + 22, 8 + bob], fill=yh)
        d.polygon([(x0 + 27, 10 + bob), (x0 + 32, 12 + bob), (x0 + 27, 14 + bob)], fill=beak)
        d.ellipse([x0 + 22, 7 + bob, x0 + 25, 10 + bob], fill=OUTLINE)
        d.line([x0 + 21, 6 + bob, x0 + 26, 7 + bob], fill=OUTLINE)
    x0 = W * 2
    d.ellipse([x0 + 3, 22, x0 + 29, 31], fill=OUTLINE)
    d.ellipse([x0 + 4, 23, x0 + 28, 30], fill=yl)
    img.save(OUT / "enemy-patinho.png")

    # capivara (quartel), olhando para a direita
    img = Image.new("RGBA", (W * 3, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fur, furh, furd, nose = (150, 102, 62), (190, 140, 92), (104, 68, 40), (70, 48, 34)
    for f in range(2):
        x0, bob = f * W, f
        # patinhas
        for i, lx in enumerate((7, 12, 19, 24)):
            off = 1 if (i + f) % 2 else -1
            d.line([x0 + lx, 24, x0 + lx + off, 30], fill=OUTLINE, width=3)
            d.point((x0 + lx + off, 30), fill=furd)
        # corpo de barril
        d.rounded_rectangle([x0 + 2, 11 + bob, x0 + 27, 27], radius=8, fill=OUTLINE)
        d.rounded_rectangle([x0 + 3, 12 + bob, x0 + 26, 26], radius=7, fill=fur)
        d.rounded_rectangle([x0 + 5, 13 + bob, x0 + 20, 17 + bob], radius=3, fill=furh)
        d.line([x0 + 4, 25, x0 + 25, 25], fill=furd)
        # cabecao quadrado com focinho
        d.rounded_rectangle([x0 + 18, 7 + bob, x0 + 31, 21 + bob], radius=4, fill=OUTLINE)
        d.rounded_rectangle([x0 + 19, 8 + bob, x0 + 30, 20 + bob], radius=3, fill=fur)
        d.rectangle([x0 + 27, 13 + bob, x0 + 30, 19 + bob], fill=nose)
        d.point((x0 + 29, 14 + bob), fill=(20, 14, 10))
        d.rectangle([x0 + 23, 11 + bob, x0 + 24, 12 + bob], fill=OUTLINE)  # olho
        d.point((x0 + 24, 11 + bob), fill=(255, 255, 255))
        d.rectangle([x0 + 20, 5 + bob, x0 + 22, 8 + bob], fill=OUTLINE)  # orelhinha
        d.point((x0 + 21, 6 + bob), fill=furh)
        d.line([x0 + 26, 18 + bob, x0 + 28, 18 + bob], fill=furd)  # sorriso
    x0 = W * 2  # amassada
    d.rounded_rectangle([x0 + 2, 22, x0 + 30, 31], radius=4, fill=OUTLINE)
    d.rounded_rectangle([x0 + 3, 23, x0 + 29, 30], radius=3, fill=fur)
    d.rectangle([x0 + 25, 25, x0 + 28, 28], fill=nose)
    img.save(OUT / "enemy-capivara.png")

    # aviaozinho de papel (escolinha): voa, nao anda
    img = Image.new("RGBA", (W * 3, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    paper, fold, shade = (250, 250, 246), (210, 214, 222), (160, 166, 180)
    for f in range(3):
        x0 = f * W
        tilt = [0, 2, 0][f]
        if f == 2:  # amassado
            d.polygon([(x0 + 8, 26), (x0 + 16, 20), (x0 + 25, 25), (x0 + 18, 30), (x0 + 10, 30)], fill=paper, outline=OUTLINE)
            d.line([x0 + 12, 24, x0 + 20, 28], fill=shade)
            continue
        d.polygon([(x0 + 2, 10 + tilt), (x0 + 30, 16), (x0 + 12, 18 + tilt)], fill=paper, outline=OUTLINE)
        d.polygon([(x0 + 12, 18 + tilt), (x0 + 30, 16), (x0 + 10, 24 - tilt)], fill=fold, outline=OUTLINE)
        d.line([x0 + 12, 18 + tilt, x0 + 30, 16], fill=shade)
        d.ellipse([x0 + 18, 13, x0 + 21, 16], fill=OUTLINE)  # olhinho bravo
        d.line([x0 + 17, 11, x0 + 22, 13], fill=OUTLINE)
        d.line([x0 + 3, 20 + tilt, x0 + 8, 20 + tilt], fill=(120, 170, 230))
        d.line([x0 + 1, 23 + tilt, x0 + 6, 23 + tilt], fill=(120, 170, 230))
    img.save(OUT / "enemy-aviao.png")


if __name__ == "__main__":
    for theme in THEMES:
        make_theme_tiles(theme)
    make_springs()
    make_theme_enemies()
    print("temas ok")
