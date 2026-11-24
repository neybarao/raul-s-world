"""Transforma o character sheet de referencia em sprites de pixel art nitidos.

Uso: python3 tools/pixelize_reference.py

Passos: recorta cada pose do sheet, tira o fundo, reduz TODAS as poses com a mesma escala,
reduz as cores para uma paleta unica e firma o contorno com 1 pixel escuro.
Isso mantem a cara do Raul da referencia, sem o borrado de uma simples reducao de imagem.
"""
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw

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

# Escala "32 bits": personagem grande, muitas cores, sombreado suave e contorno colorido.
U = 2                       # multiplicador em relacao a versao 16 bits
RAUL_SCALE = 34 * U / 368   # o Raul parado fica com 68 px de altura
DOG_SCALE = 19 * U / 190    # o cachorro andando fica com 38 px
RAUL_FRAME = (32 * U, 44 * U)
DOG_FRAME = (26 * U, 20 * U)
RAUL_COLORS = 64
DOG_COLORS = 32
COIN = (985, 825, 1055, 925)
FLAG = (1366, 740, 1505, 975)


# ---------- recorte e fundo ----------

def is_bg(px):
    r, g, b = px[:3]
    return min(r, g, b) > 150 and (max(r, g, b) - min(r, g, b)) < 40


def cut(sheet, box):
    return cut_img(sheet.crop(box))


def cut_img(img):
    img = img.convert("RGBA")
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
    # pixels de lagrima (azul forte) nao passam pela paleta, senao viram cinza
    src, dst = img.load(), out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            if a and b > r + 50 and b > 150:
                dst[x, y] = TEAR_HI if g > 215 else TEAR
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
                # contorno colorido (estilo 32 bits): a propria cor bem escurecida
                dst[x, y] = (int(OUTLINE[0] * 0.55 + r * 0.25), int(OUTLINE[1] * 0.55 + g * 0.25), int(OUTLINE[2] * 0.55 + b * 0.25), 255)
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


# pecas da pose sentada, em coordenadas do sheet
TORSO = (425, 280, 615, 410)       # tronco e bermuda do Raul parado
BACK_SHOE = (955, 360, 1013, 448)  # tenis de tras da corrida; espelhado fica de bico para cima


def crying_face(sheet, variant):
    """Rosto triste com lagrimas pintadas em resolucao cheia (antes de reduzir)."""
    face = sheet.crop(FACE_SAD).convert("RGBA")
    d = ImageDraw.Draw(face)
    length = 46 if variant == 0 else 34
    drop = 0 if variant == 0 else 18
    for ex, ey in ((96, 156), (160, 159)):
        d.rounded_rectangle([ex - 6, ey, ex + 6, ey + length], radius=6, fill=TEAR)
        d.rounded_rectangle([ex - 3, ey + 2, ex, ey + length - 6], radius=2, fill=TEAR_HI)
        if drop:  # gota caindo separada
            d.ellipse([ex - 6, ey + length + drop, ex + 6, ey + length + drop + 14], fill=TEAR)
    return cut_img(face)


def sitting(sheet, idle_w, variant):
    """Raul sentado no chao, olhando para a direita, com as pernas esticadas e chorando."""
    face = crying_face(sheet, variant)
    torso = cut(sheet, TORSO)
    shoe = cut(sheet, BACK_SHOE).transpose(Image.FLIP_LEFT_RIGHT)
    scale = idle_w * 0.98 / face.width
    face = face.resize((int(face.width * scale), int(face.height * scale)), Image.LANCZOS)
    bob = 0 if variant == 0 else 6  # ombros sobem no soluco
    torso_y = face.height - 22 + bob
    ground = torso_y + torso.height + 4
    shin_x0 = int(torso.width * 0.45)
    shoe_x = int(torso.width * 0.80)
    w = max(torso.width, shoe_x + shoe.width, face.width)
    out = Image.new("RGBA", (w, ground), (0, 0, 0, 0))
    out.alpha_composite(torso, (0, torso_y))
    # canela esticada no chao, com contorno e sombra embaixo
    d = ImageDraw.Draw(out)
    top = ground - 46
    d.rounded_rectangle([shin_x0, top, shoe_x + 24, ground - 2], radius=18, fill=(244, 178, 128, 255), outline=(40, 20, 14, 255), width=6)
    d.rounded_rectangle([shin_x0 + 8, ground - 18, shoe_x + 16, ground - 9], radius=4, fill=(214, 140, 96, 255))
    d.rounded_rectangle([shin_x0 + 10, top + 9, shoe_x + 10, top + 16], radius=4, fill=(254, 214, 172, 255))
    # meia branca
    d.rectangle([shoe_x + 4, top + 6, shoe_x + 20, ground - 8], fill=(246, 246, 246, 255))
    out.alpha_composite(shoe, (shoe_x, ground - shoe.height))
    out.alpha_composite(face, ((torso.width - face.width) // 2, bob))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(SHEET)

    raul_full = {k: cut(sheet, b) for k, b in RAUL.items()}
    sad = cut(sheet, FACE_SAD)
    raul_full["hurt"] = head_swap(raul_full["jump"], sad, 0.43, raul_full["idle"].width * 0.98)
    raul_full["cry1"] = sitting(sheet, raul_full["idle"].width, 0)
    raul_full["cry2"] = sitting(sheet, raul_full["idle"].width, 1)

    order = ["idle", "run1", "run2", "jump", "hurt", "cry1", "cry2"]
    small = [shrink(raul_full[k], RAUL_SCALE) for k in order]
    pal = build_palette(small, RAUL_COLORS)
    frames = [outline(apply_palette(s, pal)) for s in small]
    # ordem final: 0 parado, 1 corrida1, 2 corrida2, 3 pulo, 4 dano, 5 choro1, 6 choro2
    place(frames, *RAUL_FRAME).save(OUT / "raul.png")
    print("raul", [f.size for f in frames])

    dog_small = [shrink(cut(sheet, DOG[k]), DOG_SCALE) for k in ("walk", "run", "sit", "sleep")]
    dpal = build_palette(dog_small, DOG_COLORS)
    dog_frames = [outline(apply_palette(s, dpal)) for s in dog_small]
    place(dog_frames, *DOG_FRAME).save(OUT / "dog.png")
    print("dog", [f.size for f in dog_frames])

    face = shrink(cut(sheet, FACE_HAPPY), 24 * U / 236)
    outline(apply_palette(face, build_palette([face], 48))).save(OUT / "raul-face.png")

    for name, box, height, colors in (("coin", COIN, 14 * U, 16), ("flag", FLAG, 56 * U, 24)):
        img = cut(sheet, box)
        small = shrink(img, height / img.height)
        outline(apply_palette(small, build_palette([small], colors))).save(OUT / f"{name}.png")


if __name__ == "__main__":
    main()
