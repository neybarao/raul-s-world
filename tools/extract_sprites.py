"""Recorta sprites placeholder do character sheet conceitual.

Uso: python3 tools/extract_sprites.py
Gera PNGs com fundo transparente em public/assets/sprites/.
Esses sprites sao provisorios: a arte final deve ser desenhada em grade de pixels real.
"""
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "art/concept/character-sheet.png"
OUT = ROOT / "public/assets/sprites"

# (nome, caixa no sheet x0, y0, x1, y1, altura final em px)
CROPS = [
    ("raul-idle", (425, 105, 615, 478), 32),
    ("raul-run1", (685, 115, 915, 478), 32),
    ("raul-run2", (955, 110, 1215, 478), 32),
    ("raul-jump", (1250, 15, 1505, 478), 34),
    ("raul-face", (45, 510, 255, 750), 24),
    ("dog-walk", (35, 775, 245, 975), 18),
    ("dog-run", (290, 775, 525, 975), 18),
    ("dog-sit", (555, 785, 715, 975), 20),
    ("dog-sleep", (735, 845, 950, 975), 13),
    ("coin", (985, 825, 1055, 925), 14),
    ("flag", (1366, 740, 1505, 975), 56),
]


def is_bg(px):
    r, g, b = px[:3]
    mx, mn = max(r, g, b), min(r, g, b)
    # fundo creme, sombras acinzentadas e poeira clara: pouca saturacao
    return mn > 150 and (mx - mn) < 40


def remove_bg(img):
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    seen = set()
    q = deque()
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        seen.add((x, y))
        if not is_bg(px[x, y]):
            continue
        px[x, y] = (0, 0, 0, 0)
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return img


def keep_main_blob(img, min_ratio=0.02):
    """Apaga manchas soltas (poeira, riscos de movimento) fora do corpo principal."""
    w, h = img.size
    px = img.load()
    seen = set()
    blobs = []
    for sy in range(h):
        for sx in range(w):
            if (sx, sy) in seen or px[sx, sy][3] == 0:
                continue
            blob, q = [], deque([(sx, sy)])
            seen.add((sx, sy))
            while q:
                x, y = q.popleft()
                blob.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and px[nx, ny][3]:
                        seen.add((nx, ny))
                        q.append((nx, ny))
            blobs.append(blob)
    biggest = max(len(b) for b in blobs)
    for b in blobs:
        if len(b) < biggest * min_ratio:
            for x, y in b:
                px[x, y] = (0, 0, 0, 0)
    return img


def downscale(img, target_h):
    img = keep_main_blob(img)
    bbox = img.getbbox()
    img = img.crop(bbox)
    w, h = img.size
    target_w = max(1, round(w * target_h / h))
    # reduz com media de area e depois binariza o alfa para ficar com cara de pixel
    small = img.resize((target_w, target_h), Image.BOX)
    p = small.load()
    for y in range(target_h):
        for x in range(target_w):
            r, g, b, a = p[x, y]
            if a < 110:
                p[x, y] = (0, 0, 0, 0)
            else:
                k = 255 / a
                p[x, y] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), 255)
    return small


# spritesheets com quadros de tamanho igual, alinhados pelo pe e centralizados
SHEETS = {
    "raul": (["raul-idle", "raul-run1", "raul-run2", "raul-jump"], 26, 34),
    "dog": (["dog-walk", "dog-run", "dog-sit", "dog-sleep"], 24, 20),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(SHEET)
    frames = {}
    for name, box, h in CROPS:
        sprite = downscale(remove_bg(sheet.crop(box)), h)
        frames[name] = sprite
        if name in ("raul-face", "coin", "flag"):
            sprite.save(OUT / f"{name}.png")
        print(name, sprite.size)
    for sheet_name, (names, fw, fh) in SHEETS.items():
        out = Image.new("RGBA", (fw * len(names), fh), (0, 0, 0, 0))
        for i, n in enumerate(names):
            f = frames[n]
            out.alpha_composite(f, (i * fw + (fw - f.width) // 2, fh - f.height))
        out.save(OUT / f"{sheet_name}.png")
        print(sheet_name, out.size)


if __name__ == "__main__":
    main()
