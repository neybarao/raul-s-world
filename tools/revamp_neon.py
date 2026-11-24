"""Revamp visual "neon": cores mais vivas e modernas em cima da arte atual.

Uso: python3 tools/revamp_neon.py  (depois rode python3 tools/make_thumbs.py)

Nao redesenha nada: o Raul, o cachorro e a mamae continuam fieis ao character sheet.
O script so regrada as cores e acrescenta o acabamento do estilo neon:
- fundos (art/backgrounds/*.jpg): saturacao alta, sombras puxadas para o roxo/indigo,
  luzes quentes e ceu de entardecer violeta no alto
- sprites (art/classic/): cores mais saturadas, sombras arroxeadas e contorno externo
  branco de 1 pixel (o "adesivo" brilhante dos personagens da referencia)
- tiles (art/classic/): cores vivas e uma linha de luz neon na beirada de cima
- moeda: halo dourado em degraus de transparencia (continua pixel art)

As entradas ficam em art/classic/ (copia da arte antes do revamp), entao rodar de novo
nao acumula o efeito. As saidas vao para public/assets/.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CLASSIC = ROOT / "art/classic"
BG_SRC = ROOT / "art/backgrounds"
OUT = ROOT / "public/assets"

INDIGO = np.array([34, 16, 92], float)      # sombra arroxeada
WARM = np.array([255, 214, 150], float)     # luz quente
OUTLINE_GLOW = (255, 246, 255, 255)         # contorno externo dos sprites

# cor da linha neon no topo do chao de cada fase
ACCENT = {
    "tiles": (92, 242, 255),
    "tiles-aquario": (92, 242, 255),
    "tiles-bolinhas": (255, 79, 216),
    "tiles-parque": (92, 242, 255),
    "tiles-praia": (255, 210, 63),
    "tiles-quartel": (157, 255, 79),
    "tiles-escolinha": (255, 157, 63),
}
INDOOR = {"aquario", "bolinhas", "escolinha"}

# quadros de cada folha de sprites (largura, altura)
SHEETS = {
    "sprites/raul.png": (64, 88),
    "sprites/dog.png": (52, 40),
    "sprites/mamae.png": (88, 112),
    "sprites/raul-face.png": None,
    "sprites/flag.png": None,
    "hearts.png": (18, 16),
    "enemy.png": (32, 28),
}
for name in ("aguaviva", "aviao", "bola", "capivara", "caranguejo", "patinho"):
    SHEETS[f"enemy-{name}.png"] = (32, 32)
for name in ("aquario", "bolinhas", "escolinha", "floresta", "parque", "praia", "quartel"):
    SHEETS[f"mola-{name}.png"] = (32, 24)


# ---------- cor ----------

def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rm = m & (mx == r)
    gm = m & (mx == g) & ~rm
    bm = m & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = (b - r)[gm] / d[gm] + 2
    h[bm] = (r - g)[bm] / d[bm] + 4
    h /= 6
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return np.stack([h, s, mx], -1)


def hsv_to_rgb(hsv):
    h, s, v = hsv[..., 0] * 6, hsv[..., 1], hsv[..., 2]
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros(hsv.shape)
    for k, (a, b, c) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        sel = i == k
        out[sel] = np.stack([a[sel], b[sel], c[sel]], -1)
    return out


def grade(rgb, sat=1.35, contrast=1.08, shadow=0.30, warm=0.10):
    """rgb float 0..255 -> rgb float. Saturacao, contraste, sombra roxa e luz quente."""
    hsv = rgb_to_hsv(rgb / 255.0)
    hsv[..., 1] = np.clip(hsv[..., 1] * sat, 0, 1)
    out = hsv_to_rgb(hsv) * 255
    out = (out - 128) * contrast + 128
    lum = (0.299 * out[..., 0] + 0.587 * out[..., 1] + 0.114 * out[..., 2]) / 255
    lum = np.clip(lum, 0, 1)[..., None]
    sw = np.clip(1 - lum * 2.2, 0, 1) * shadow           # so nos tons escuros
    out = out * (1 - sw) + INDIGO * sw
    hw = np.clip(lum * 2 - 1.1, 0, 1) * warm              # so nas luzes fortes
    out = out * (1 - hw) + WARM * hw
    return np.clip(out, 0, 255)


def grade_rgba(img, **kw):
    a = np.asarray(img.convert("RGBA")).astype(float)
    a[..., :3] = grade(a[..., :3], **kw)
    return Image.fromarray(a.round().astype(np.uint8), "RGBA")


# ---------- sprites ----------

def outline(frame):
    """Contorno externo de 1 pixel (4 vizinhos) em volta de tudo que e opaco."""
    a = np.asarray(frame).copy()
    solid = a[..., 3] > 0
    grow = np.zeros_like(solid)
    grow[1:, :] |= solid[:-1, :]
    grow[:-1, :] |= solid[1:, :]
    grow[:, 1:] |= solid[:, :-1]
    grow[:, :-1] |= solid[:, 1:]
    ring = grow & ~solid
    a[ring] = OUTLINE_GLOW
    clipped = solid[0].any() or solid[:, 0].any() or solid[:, -1].any()
    return Image.fromarray(a, "RGBA"), clipped


def make_sprite(rel, frame):
    src = Image.open(CLASSIC / rel).convert("RGBA")
    img = grade_rgba(src, sat=1.3, contrast=1.06, shadow=0.35, warm=0.06)
    fw, fh = frame or img.size
    out = Image.new("RGBA", img.size)
    touched = 0
    for x in range(0, img.width, fw):
        f, clip = outline(img.crop((x, 0, x + fw, fh)))
        out.paste(f, (x, 0))
        touched += clip
    out.save(OUT / rel, optimize=True)
    note = f" ({touched} quadro(s) encostam no topo ou nos lados)" if touched else ""
    print("sprite", rel, img.size, note)


def make_coin():
    """Moeda mais viva com halo dourado em degraus (4 px de folga em cada lado)."""
    src = grade_rgba(Image.open(CLASSIC / "sprites/coin.png"), sat=1.25, contrast=1.1, shadow=0.2, warm=0.25)
    src, _ = outline(src)
    pad = 4
    w, h = src.width + pad * 2, src.height + pad * 2
    a = np.zeros((h, w), float)
    a[pad:pad + src.height, pad:pad + src.width] = np.asarray(src)[..., 3] > 0
    yy, xx = np.mgrid[0:h, 0:w]
    pts = np.argwhere(a > 0)
    dist = np.full((h, w), 99.0)
    for y, x in pts[:: max(1, len(pts) // 400)]:
        dist = np.minimum(dist, np.hypot(yy - y, xx - x))
    halo = np.zeros((h, w, 4), np.uint8)
    for r, alpha in ((4.2, 40), (2.8, 90), (1.5, 150)):  # aneis de fora para dentro
        ring = dist <= r
        halo[ring] = (255, 214, 80, alpha)
    out = Image.fromarray(halo, "RGBA")
    out.alpha_composite(src, (pad, pad))
    out.save(OUT / "sprites/coin.png", optimize=True)
    print("moeda", out.size)


# ---------- tiles ----------

TOPS = (0, 2, 3, 6, 7, 8)  # tiles com superficie em cima (grama e plataformas)


def extrude(img):
    """Refaz a margem de 1 px e o espaco de 2 px copiando as bordas de cada tile."""
    a = np.asarray(img).copy()
    for i in range(9):
        x0 = 1 + i * 34
        a[0, x0:x0 + 32] = a[1, x0:x0 + 32]
        a[33, x0:x0 + 32] = a[32, x0:x0 + 32]
        a[:, x0 - 1] = a[:, x0]
        a[:, x0 + 32] = a[:, x0 + 31]
    return Image.fromarray(a, "RGBA")


def make_tiles(name):
    img = grade_rgba(Image.open(CLASSIC / f"{name}.png"), sat=1.45, contrast=1.08, shadow=0.38, warm=0.08)
    a = np.asarray(img).astype(float)
    acc = np.array(ACCENT[name], float)
    for i in TOPS:
        x0 = 1 + i * 34
        # so onde o tile e opaco na linha de cima (plataformas finas nao comecam no y=0)
        for x in range(x0, x0 + 32):
            col = np.nonzero(a[1:33, x, 3] > 0)[0]
            if not len(col):
                continue
            y = 1 + col[0]
            a[y, x, :3] = acc * 0.45 + 255 * 0.55              # brilho quase branco
            a[y + 1, x, :3] = a[y + 1, x, :3] * 0.3 + acc * 0.7  # cor neon
    out = extrude(Image.fromarray(a.round().astype(np.uint8), "RGBA"))
    out.save(OUT / f"{name}.png", optimize=True)
    print("tiles", name)


# ---------- fundos ----------

# rampa do entardecer neon: indigo -> violeta -> magenta -> laranja -> creme
RAMP = np.array([[18, 8, 58], [62, 22, 140], [150, 40, 190], [255, 80, 170], [255, 170, 90], [255, 240, 190]], float)


def gradient_map(lum):
    x = lum * (len(RAMP) - 1)
    i = np.clip(np.floor(x).astype(int), 0, len(RAMP) - 2)
    f = (x - i)[..., None]
    return RAMP[i] * (1 - f) + RAMP[i + 1] * f


def make_background(src):
    img = np.asarray(Image.open(src).convert("RGB")).astype(float)
    indoor = src.stem in INDOOR
    hsv = rgb_to_hsv(img / 255)
    h = hsv[..., 0]
    # azuis do ceu e da agua giram um pouco para o violeta
    blue = (h > 0.5) & (h < 0.7)
    hsv[..., 0] = np.where(blue, h + 0.10 * np.clip((h - 0.5) / 0.1, 0, 1), h)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.5 + 0.04, 0, 1)
    hsv[..., 2] = np.clip((hsv[..., 2] - 0.5) * 1.18 + 0.52, 0, 1)
    out = hsv_to_rgb(hsv) * 255
    lum = np.clip((0.299 * out[..., 0] + 0.587 * out[..., 1] + 0.114 * out[..., 2]) / 255, 0, 1)
    # mistura com a rampa so nas sombras (ficam roxas, as cores claras continuam vivas)
    # e no alto do panorama (ceu de entardecer)
    H = img.shape[0]
    t = np.clip(1 - np.arange(H) / (H * 0.55), 0, 1)[:, None]
    w = 0.6 * np.clip(1 - lum * 1.7, 0, 1) + (0.12 if indoor else 0.30) * t ** 1.3
    w = np.clip(w, 0, 0.75)[..., None]
    out = out * (1 - w) + gradient_map(lum) * w
    q = Image.fromarray(np.clip(out, 0, 255).round().astype(np.uint8), "RGB")
    q = q.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    mirrored = Image.new("RGB", (q.width * 2, q.height))
    mirrored.paste(q, (0, 0))
    mirrored.paste(q.transpose(Image.FLIP_LEFT_RIGHT), (q.width, 0))
    (OUT / "bg").mkdir(parents=True, exist_ok=True)
    mirrored.save(OUT / "bg" / f"{src.stem}.png", optimize=True)
    top = q.crop((0, 0, q.width, 6)).resize((1, 1), Image.BOX).getpixel((0, 0))
    print("fundo", src.stem, "cor do topo #%02x%02x%02x" % top)


def main():
    for src in sorted(BG_SRC.glob("*.jpg")):
        make_background(src)
    for name in ACCENT:
        make_tiles(name)
    for rel, frame in SHEETS.items():
        make_sprite(rel, frame)
    make_coin()


if __name__ == "__main__":
    main()
