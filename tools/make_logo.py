"""Logo do jogo (RAUL / AVENTUREIRO) para o seletor de fases.

Uso: python3 tools/make_logo.py
Entrada: art/concept/logo-source.jpg, gerada no Magnific (GPT 2.6) sobre fundo verde chapado.
Saida: public/assets/logo.png, em pixel art de verdade: tira o fundo verde, reduz pelo tamanho
do "pixel" da arte original e limita a paleta, para ficar nitida ao ampliar no jogo.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art/concept/logo-source.jpg"
OUT = ROOT / "public/assets/logo.png"
PIXEL = 6        # tamanho aproximado de cada pixel da arte original
COLORS = 32


def main():
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g > 140) & (g > r + 60) & (g > b + 60)
    rgba = np.dstack([a, np.where(green, 0, 255)]).astype(np.uint8)
    img = Image.fromarray(rgba, "RGBA")
    img = img.crop(img.getbbox())
    w, h = img.size
    small = img.resize((round(w / PIXEL), round(h / PIXEL)), Image.BOX)
    s = np.asarray(small).astype(float)
    alpha = s[..., 3] > 140
    # tira o verde que vazou na borda (mistura com o fundo) puxando para a cor do contorno
    rgb = s[..., :3] / np.maximum(s[..., 3:4] / 255, 1e-3)
    rgb = np.clip(rgb, 0, 255)
    spill = rgb[..., 1] > np.maximum(rgb[..., 0], rgb[..., 2]) + 30
    rgb[spill] = (20, 22, 70)
    rgb_img = Image.fromarray(rgb.astype(np.uint8), "RGB")
    q = rgb_img.quantize(colors=COLORS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGBA")
    out = np.asarray(q).copy()
    out[..., 3] = np.where(alpha, 255, 0)
    Image.fromarray(out, "RGBA").save(OUT, optimize=True)
    print(OUT.relative_to(ROOT), (out.shape[1], out.shape[0]))


if __name__ == "__main__":
    main()
