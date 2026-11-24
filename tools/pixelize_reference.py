"""Transforma o character sheet de referencia em sprites de pixel art nitidos.

Uso: python3 tools/pixelize_reference.py

Passos: recorta cada pose do sheet, tira o fundo, reduz TODAS as poses com a mesma escala,
reduz as cores para uma paleta unica e firma o contorno com 1 pixel escuro.
Isso mantem a cara do Raul da referencia, sem o borrado de uma simples reducao de imagem.
"""
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "art/concept/character-sheet.png"
OUT = ROOT / "public/assets/sprites"

OUTLINE = (52, 28, 20, 255)
TEAR = (96, 186, 246, 255)
TEAR_HI = (200, 238, 255, 255)

# poses no sheet (x0, y0, x1, y1)
RAUL = {
    "idle": (425, 105, 615, 478),
    "run1": (685, 115, 915, 478),
    "run2": (955, 110, 1215, 478),
    "jump": (1250, 15, 1505, 478),
}
FACE_SAD = (1040, 510, 1255, 712)    # cabeca triste (sem a camiseta)
FACE_HAPPY = (45, 510, 255, 750)     # rosto do HUD
DOG = {
    "walk": (35, 775, 245, 975),
    "run": (290, 775, 525, 975),
    "sit": (555, 785, 715, 975),
    "sleep": (735, 845, 950, 975),
}

RAUL_SCALE = 34 / 368   # o Raul parado fica com 34 px de altura
DOG_SCALE = 19 / 190    # o cachorro andando fica com 19 px
RAUL_FRAME = (32, 44)
DOG_FRAME = (26, 20)


# ---------- recorte e fundo ----------

def is_bg(px):
    r, g, b = px[:3]
    return min(r, g, b) > 150 and (max(r, g, b) - min(r, g, b)) < 40


def cut(sheet, box):
    img = sheet.crop(box).convert("RGBA")
    w, h = img.size
    px = img.load()
    seen = set()
    q = deque([(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)])
    while q:
        x, y = q.popleft()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        seen.add((x, y))
        if not is_bg(px[x, y]):
            continue
        px[x, y] = (0, 0, 0, 0)
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return keep_main_blob(img)


def keep_main_blob(img, min_ratio=0.03):
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
    return img.crop(img.getbbox())


# ---------- reducao para pixel art ----------

def shrink(img, scale):
    w, h = img.size
    tw, th = max(1, round(w * scale)), max(1, round(h * scale))
    small = img.resize((tw, th), Image.BOX)
    p = small.load()
    for y in range(th):
        for x in range(tw):
            r, g, b, a = p[x, y]
            if a < 120:
                p[x, y] = (0, 0, 0, 0)
            else:
                k = 255 / a
                p[x, y] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), 255)
    return small


def build_palette(images, colors):
    """Paleta unica para todos os quadros, assim as cores nao variam entre poses."""
    w = sum(i.width for i in images)
    h = max(i.height for i in images)
    strip = Image.new("RGB", (w, h), (0, 0, 0))
    x = 0
    mask_px = []
    for i in images:
        rgb = Image.new("RGB", i.size, (0, 0, 0))
        rgb.paste(i, (0, 0), i)
        strip.paste(rgb, (x, 0))
        x += i.width
    # so pixels opacos contam para a paleta
    opaque = [i.getpixel((x, y)) for i in images for y in range(i.height) for x in range(i.width) if i.getpixel((x, y))[3]]
    sample = Image.new("RGB", (len(opaque), 1))
    sample.putdata([p[:3] for p in opaque])
    return sample.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)


def apply_palette(img, pal_img):
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    q = rgb.quantize(palette=pal_img, dither=Image.Dither.NONE).convert("RGBA")
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(q, (0, 0), img.split()[3].point(lambda a: 255 if a else 0))
    return out


def outline(img):
    """Escurece a borda externa: pixel opaco encostado no transparente vira contorno."""
    w, h = img.size
    src = img.load()
    out = img.copy()
    dst = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                continue
            edge = any(
                not (0 <= nx < w and 0 <= ny < h) or src[nx, ny][3] == 0
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
            )
            if edge:
                r, g, b, _ = src[x, y]
                # mantem o contorno escuro, mas puxa a cor original para nao ficar chapado
                dst[x, y] = (int(OUTLINE[0] * 0.8 + r * 0.2), int(OUTLINE[1] * 0.8 + g * 0.2), int(OUTLINE[2] * 0.8 + b * 0.2), 255)
    return out


def place(frames, fw, fh):
    sheet = Image.new("RGBA", (fw * len(frames), fh), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        assert f.width <= fw and f.height <= fh, (i, f.size)
        sheet.alpha_composite(f, (i * fw + (fw - f.width) // 2, fh - f.height))
    return sheet


# ---------- poses montadas ----------

def head_swap(body, face, head_h_ratio, head_w):
    """Troca a cabeca de uma pose pela cabeca de uma expressao (em resolucao cheia)."""
    head_h = int(body.height * head_h_ratio)
    scale = head_w / face.width
    f = face.resize((int(face.width * scale), int(face.height * scale)), Image.LANCZOS)
    out = Image.new("RGBA", (max(body.width, f.width), body.height + max(0, f.height - head_h)), (0, 0, 0, 0))
    oy = out.height - body.height
    lower = body.crop((0, head_h - 10, body.width, body.height))
    out.alpha_composite(lower, (0, oy + head_h - 10))
    out.alpha_composite(f, ((out.width - f.width) // 2, 0))
    return out


def sitting(idle, face):
    """Raul sentado: cabeca triste, tronco e bermuda, tenis logo abaixo (pernas encolhidas)."""
    w, h = idle.size
    torso = idle.crop((0, int(h * 0.47), w, int(h * 0.80)))
    shoes = idle.crop((0, int(h * 0.88), w, h))
    scale = (w * 0.98) / face.width
    f = face.resize((int(face.width * scale), int(face.height * scale)), Image.LANCZOS)
    total = f.height - 14 + torso.height + shoes.height - 18
    out = Image.new("RGBA", (w, total), (0, 0, 0, 0))
    y = f.height - 14
    out.alpha_composite(torso, (0, y))
    out.alpha_composite(shoes, (0, y + torso.height - 18))
    out.alpha_composite(f, ((w - f.width) // 2, 0))
    return out


def legs_forward(img):
    """Tira os tenis de baixo e desenha as pernas esticadas no chao, para a direita."""
    w, h = img.size
    p = img.load()
    # bermuda termina onde comecam os tenis; corta as ultimas linhas
    cut_rows = 3
    body = img.crop((0, 0, w, h - cut_rows))
    bw, bh = body.size
    out = Image.new("RGBA", (w + 7, bh + 1), (0, 0, 0, 0))
    out.alpha_composite(body, (0, 0))
    q = out.load()
    SKIN, SKIN_D = (240, 176, 128, 255), (206, 136, 96, 255)
    SHOE, SOLE = (214, 46, 40, 255), (246, 246, 246, 255)
    # bermuda encostada no chao: fecha a base com contorno
    y0 = bh - 2
    x_start = bw - 4
    for x in range(x_start, w + 3):
        q[x, y0 - 1] = OUTLINE if q[x, y0 - 1][3] == 0 else q[x, y0 - 1]
        q[x, y0] = SKIN
        q[x, y0 + 1] = SKIN_D
        q[x, y0 + 2] = OUTLINE
    # tenis na ponta
    for dy in range(-3, 3):
        for dx in range(4):
            x, y = w + 3 + dx, y0 + dy
            if dy == -3 or dx == 3 or dy == 2:
                q[x, y] = OUTLINE
            elif dy == 1:
                q[x, y] = SOLE
            else:
                q[x, y] = SHOE
    q[w + 2, y0 - 1] = OUTLINE
    return out


def add_tears(img, variant):
    """Lagrimas desenhadas ja em pixel, abaixo dos olhos."""
    out = img.copy()
    p = out.load()
    w, h = out.size
    # olhos ficam por volta de 40% da altura da cabeca e 35%/68% da largura
    ey = int(h * 0.30)
    for ex in (int(w * 0.36), int(w * 0.66)):
        drops = [(0, 1), (0, 2), (0, 3)] if variant == 0 else [(0, 2), (0, 3), (0, 4)]
        for dx, dy in drops:
            x, y = ex + dx, ey + dy
            if 0 <= x < w and 0 <= y < h and p[x, y][3]:
                p[x, y] = TEAR
        x, y = ex, ey + drops[0][1]
        if p[x, y][3]:
            p[x, y] = TEAR_HI
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(SHEET)

    raul_full = {k: cut(sheet, b) for k, b in RAUL.items()}
    sad = cut(sheet, FACE_SAD)
    raul_full["hurt"] = head_swap(raul_full["jump"], sad, 0.43, raul_full["idle"].width * 0.98)
    raul_full["sit"] = sitting(raul_full["idle"], sad)

    order = ["idle", "run1", "run2", "jump", "hurt", "sit"]
    small = [shrink(raul_full[k], RAUL_SCALE) for k in order]
    pal = build_palette(small, 22)
    frames = [outline(apply_palette(s, pal)) for s in small]
    sit = legs_forward(frames[5])
    frames[5] = add_tears(sit, 0)
    frames.append(add_tears(sit, 1))
    # ordem final: 0 parado, 1 corrida1, 2 corrida2, 3 pulo, 4 dano, 5 choro1, 6 choro2
    place(frames, *RAUL_FRAME).save(OUT / "raul.png")
    print("raul", [f.size for f in frames])

    dog_small = [shrink(cut(sheet, DOG[k]), DOG_SCALE) for k in ("walk", "run", "sit", "sleep")]
    dpal = build_palette(dog_small, 12)
    dog_frames = [outline(apply_palette(s, dpal)) for s in dog_small]
    place(dog_frames, *DOG_FRAME).save(OUT / "dog.png")
    print("dog", [f.size for f in dog_frames])

    face = shrink(cut(sheet, FACE_HAPPY), 24 / 236)
    fpal = build_palette([face], 16)
    outline(apply_palette(face, fpal)).save(OUT / "raul-face.png")


if __name__ == "__main__":
    main()
