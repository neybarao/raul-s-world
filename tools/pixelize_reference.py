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
    "idle": (425, 100, 648, 482),
    "run1": (686, 105, 921, 482),
    "run2": (961, 100, 1228, 482),
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
# ciclo de corrida: quadros de um video do Raul correndo no lugar (Magnific, Seedance 2.0 Mini),
# numa folha 4x4 com legenda de tempo embaixo de cada quadro; um ciclo = os 8 primeiros
RUN_SHEET = ROOT / "art/concept/run-cycle-video.jpg"
RUN_GRID = (4, 4)
RUN_CELL_IMG_H = 338   # altura da imagem em cada celula (o resto e a legenda)
RUN_FRAMES = 8
# Raul sentado chorando: 2 quadros lado a lado, gerados no Magnific (GPT 2.6)
CRY_SHEET = ROOT / "art/concept/cry-sheet.jpg"
CRY_HEIGHT = 56  # sentado ele fica mais baixo que em pe (66)
# Raul arremessando a bolinha: 2 quadros lado a lado (preparando, soltando), gerados no Magnific (GPT 2.6)
# a partir do character sheet
THROW_SHEET = ROOT / "art/concept/throw-sheet.jpg"
THROW_HEIGHT = 66
# Mamae: 4 quadros lado a lado (agachada x2, abracando o Raul x2), gerados no Magnific (GPT 2.6)
MOM_SHEET = ROOT / "art/concept/mamae-sheet.jpg"
# Corrida do cachorro: quadros de um video (Magnific, Seedance 2.0 Mini), mesma folha 4x4 com legendas
DOG_RUN_SHEET = ROOT / "art/concept/dog-run-video.jpg"
DOG_RUN_FRAMES = 10
# Giro no colo da mamae: uma volta completa em 16 quadros de um video (Magnific, Seedance 2.0 Mini)
MOM_SPIN_SHEET = ROOT / "art/concept/mamae-giro-video.jpg"
MOM_SPIN_FRAMES = 16
MOM_STAND_HEIGHT = 104  # em pe, segurando o Raul
MOM_FRAME = (88, 112)
COIN = (985, 825, 1055, 925)
FLAG = (1366, 740, 1505, 975)


# ---------- recorte e fundo ----------

def is_bg(px):
    r, g, b = px[:3]
    if min(r, g, b) > 150 and (max(r, g, b) - min(r, g, b)) < 40:
        return True  # fundo creme
    # sombra cinza embaixo dos pes: sem cor e de brilho medio (contorno e mais escuro, meia e mais clara)
    return (max(r, g, b) - min(r, g, b)) < 30 and 90 < (r + g + b) / 3 < 225


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


def clear_enclosed_bg(img, tol=16):
    """Apaga o fundo creme que ficou preso dentro do desenho (entre pernas, bracos)."""
    px = img.load()
    bg = (248, 241, 230)
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and abs(r - bg[0]) < tol and abs(g - bg[1]) < tol and abs(b - bg[2]) < tol:
                px[x, y] = (0, 0, 0, 0)
    return img


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


def place(frames, fw, fh, lift=None, anchor=None):
    """Monta a tira de quadros alinhada pelo chao.
    lift[i] sobe o quadro i (voo dentro da corrida); anchor[i] e o x (dentro do quadro i) que deve
    ficar no centro, para a cabeca nao tremer de um quadro para o outro."""
    sheet = Image.new("RGBA", (fw * len(frames), fh), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        up = (lift or {}).get(i, 0)
        x = fw // 2 - round(anchor[i]) if anchor and i in anchor else (fw - f.width) // 2
        x = max(0, min(fw - f.width, x))
        assert f.width <= fw and f.height + up <= fh, (i, f.size, up)
        sheet.alpha_composite(f, (i * fw + x, fh - f.height - up))
    return sheet


def run_cycle(sheet=None, count=None, head_side="center"):
    """Recorta os quadros da corrida; devolve o desenho, a altura acima do chao e o centro da cabeca."""
    img = Image.open(sheet or RUN_SHEET).convert("RGBA")
    cols, rows = RUN_GRID
    cw, ch = img.width // cols, img.height // rows
    raw = []
    for i in range(count or RUN_FRAMES):
        r, c = divmod(i, cols)
        cell = img.crop((c * cw + 4, r * ch + 4, (c + 1) * cw - 4, r * ch + RUN_CELL_IMG_H - 4))
        fig = cut_img(cell)
        # posicao do desenho dentro da celula (camera parada: serve de referencia comum)
        rgba = cell.convert("RGBA")
        mask = Image.new("L", cell.size, 0)
        full = cut_img_keep_pos(rgba)
        box = full.getbbox()
        head = full.crop((box[0], box[1], box[2], box[1] + int((box[3] - box[1]) * 0.35))).getbbox()
        if head_side == "right":  # cachorro: a cabeca fica na frente (direita); usa a ponta do focinho
            head_cx = box[0] + head[2] - 12
        else:
            head_cx = box[0] + (head[0] + head[2]) / 2
        raw.append((fig, box[3], head_cx - box[0]))
    ground = max(b for _, b, _ in raw)
    frames = [f for f, _, _ in raw]
    lifts = [ground - b for _, b, _ in raw]
    heads = [h for _, _, h in raw]
    return frames, lifts, heads


def mom_spin():
    """Recorta a volta da mamae; devolve os desenhos e o x do centro dos pes dentro de cada um."""
    img = Image.open(MOM_SPIN_SHEET).convert("RGBA")
    cols, rows = RUN_GRID
    cw, ch = img.width // cols, img.height // rows
    frames, feet = [], []
    for i in range(MOM_SPIN_FRAMES):
        r, c = divmod(i, cols)
        cell = img.crop((c * cw + 4, r * ch + 4, (c + 1) * cw - 4, r * ch + RUN_CELL_IMG_H - 4))
        fig = clear_enclosed_bg(cut_img(cell))
        h = fig.height
        fb = fig.crop((0, int(h * 0.88), fig.width, h)).getbbox()
        frames.append(fig)
        feet.append((fb[0] + fb[2]) / 2)
    return frames, feet


def cut_img_keep_pos(img):
    """Como cut_img, mas sem recortar: o desenho fica na mesma posicao da imagem original."""
    w, h = img.size
    out = img.copy()
    px = out.load()
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
    blob = keep_main_blob(out.copy())
    return out if blob is None else _restore_pos(out)


def _restore_pos(img, min_ratio=0.03):
    """Apaga manchas soltas mantendo o tamanho e a posicao da imagem."""
    w, h = img.size
    px = img.load()
    seen, blobs = set(), []
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(SHEET)

    raul_full = {k: cut(sheet, b) for k, b in RAUL.items()}
    sad = cut(sheet, FACE_SAD)
    raul_full["hurt"] = head_swap(raul_full["jump"], sad, 0.43, raul_full["idle"].width * 0.98)
    cry = Image.open(CRY_SHEET).convert("RGBA")
    half = cry.width // 2
    raul_full["cry1"] = cut_img(cry.crop((8, 8, half - 8, cry.height - 8)))
    raul_full["cry2"] = cut_img(cry.crop((half + 8, 8, cry.width - 8, cry.height - 8)))

    # corrida: 8 quadros, na mesma altura do Raul parado (o mais alto da corrida = 66 px)
    run_full, run_lift, run_head = run_cycle()
    run_scale = 66 / max(f.height for f in run_full)
    run_small = [shrink(f, run_scale) for f in run_full]
    lift = {1 + i: round(l * run_scale) for i, l in enumerate(run_lift)}
    anchor = {1 + i: h * run_scale for i, h in enumerate(run_head)}

    order = ["idle", "jump", "hurt"]
    small = [shrink(raul_full[k], RAUL_SCALE) for k in order]
    cry_scale = CRY_HEIGHT / max(raul_full["cry1"].height, raul_full["cry2"].height)
    small += [shrink(raul_full[k], cry_scale) for k in ("cry1", "cry2")]
    small = small[:1] + run_small + small[1:]
    pal = build_palette(small, RAUL_COLORS)
    # arremesso: usa a mesma paleta (os quadros antigos ficam identicos) e alinha pela cabeca
    throw = Image.open(THROW_SHEET).convert("RGBA")
    half = throw.width // 2
    throw_full = [cut_img(throw.crop((8, 8, half - 8, throw.height - 8))),
                  cut_img(throw.crop((half + 8, 8, throw.width - 8, throw.height - 8)))]
    throw_scale = THROW_HEIGHT / max(f.height for f in throw_full)
    throw_small = [shrink(f, throw_scale) for f in throw_full]
    for i, f in enumerate(throw_small):
        head = f.crop((0, 0, f.width, int(f.height * 0.35))).getbbox()
        anchor[len(small) + i] = (head[0] + head[2]) / 2
    small += throw_small
    frames = [outline(apply_palette(s, pal)) for s in small]
    # ordem final: 0 parado, 1-8 corrida, 9 pulo, 10 dano, 11 choro1, 12 choro2,
    # 13 arremesso (preparando), 14 arremesso (soltando)
    strip = place(frames, *RAUL_FRAME, lift=lift, anchor=anchor)
    strip.save(OUT / "raul.png")
    print("raul", [f.size for f in frames])
    # onde fica a mao estendida no quadro 14 (a bolinha sai dali): ponta mais a direita na metade de cima
    fw, fh = RAUL_FRAME
    q = strip.crop((14 * fw, 0, 15 * fw, fh // 2))
    hand_x = q.getbbox()[2]
    col = [y for y in range(q.height) if q.getpixel((hand_x - 1, y))[3]]
    print("mao no quadro 14: x =", hand_x - 1, "y =", sum(col) / len(col), "(quadro 64x88, pes em y=88)")

    # parado, sentado e dormindo vem do sheet; a corrida vem do video
    dog_still = [shrink(cut(sheet, DOG[k]), DOG_SCALE) for k in ("walk", "sit", "sleep")]
    drun_full, drun_lift, drun_head = run_cycle(DOG_RUN_SHEET, DOG_RUN_FRAMES, head_side="right")
    dscale = 36 / max(f.height for f in drun_full)
    drun_small = [shrink(f, dscale) for f in drun_full]
    dog_small = dog_still + drun_small
    dpal = build_palette(dog_small, DOG_COLORS)
    dog_frames = [outline(apply_palette(s, dpal)) for s in dog_small]
    # ordem final: 0 parado, 1 sentado, 2 dormindo, 3-12 correndo
    dlift = {3 + i: round(l * dscale) for i, l in enumerate(drun_lift)}
    danchor = {3 + i: h * dscale - 6 for i, h in enumerate(drun_head)}
    place(dog_frames, *DOG_FRAME, lift=dlift, anchor=danchor).save(OUT / "dog.png")
    print("dog", [f.size for f in dog_frames])

    # mamae
    mom = Image.open(MOM_SHEET).convert("RGBA")
    cw = mom.width // 4
    mom_full = [clear_enclosed_bg(cut_img(mom.crop((i * cw + 4, 4, (i + 1) * cw - 4, mom.height - 4)))) for i in range(4)]
    mscale = MOM_STAND_HEIGHT / max(mom_full[2].height, mom_full[3].height)
    mom_small = [shrink(f, mscale) for f in mom_full]
    spin_full, spin_feet = mom_spin()
    sscale = MOM_STAND_HEIGHT / spin_full[0].height
    mom_small += [shrink(f, sscale) for f in spin_full]
    mpal = build_palette(mom_small, 72)
    mom_frames = [outline(apply_palette(f, mpal)) for f in mom_small]
    # ordem final: 0-1 agachada, 2 abraco, 3 abraco com coracao, 4-19 giro (uma volta)
    # no giro o centro dos pes fica parado no meio do quadro
    manchor = {4 + i: x * sscale + 1 for i, x in enumerate(spin_feet)}
    place(mom_frames, *MOM_FRAME, anchor=manchor).save(OUT / "mamae.png")
    print("mamae", [f.size for f in mom_frames])

    face = shrink(cut(sheet, FACE_HAPPY), 24 * U / 236)
    outline(apply_palette(face, build_palette([face], 48))).save(OUT / "raul-face.png")

    for name, box, height, colors in (("coin", COIN, 14 * U, 16), ("flag", FLAG, 56 * U, 24)):
        img = cut(sheet, box)
        small = shrink(img, height / img.height)
        outline(apply_palette(small, build_palette([small], colors))).save(OUT / f"{name}.png")


if __name__ == "__main__":
    main()
