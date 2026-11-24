"""Bolinhas de piscina de bolinhas que o Raul arremessa (botao B).

Uso: python3 tools/make_bolinhas.py
Saida: public/assets/bolinhas.png, 6 quadros de 18x18 (uma cor por quadro), desenhados pixel a pixel
com contorno, sombra embaixo e brilho em cima, no mesmo estilo dos outros sprites.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public/assets/bolinhas.png"
S = 18

# (sombra, cor, luz) de cada bolinha: vermelha, amarela, azul, verde, rosa, laranja
CORES = [
    ((150, 20, 30), (226, 44, 52), (255, 120, 120)),
    ((190, 130, 0), (255, 206, 30), (255, 240, 150)),
    ((20, 50, 150), (40, 100, 226), (130, 180, 255)),
    ((20, 120, 40), (60, 186, 70), (160, 236, 140)),
    ((170, 40, 120), (240, 90, 180), (255, 170, 220)),
    ((190, 80, 0), (255, 140, 30), (255, 200, 130)),
]
CONTORNO = (44, 26, 20, 255)


def bolinha(sombra, cor, luz):
    img = Image.new("RGBA", (S, S))
    p = img.load()
    c = (S - 1) / 2
    r = 8.2
    for y in range(S):
        for x in range(S):
            d = ((x - c) ** 2 + (y - c) ** 2) ** 0.5
            if d > r:
                continue
            if d > r - 1.1:
                p[x, y] = CONTORNO
                continue
            # luz vindo de cima a esquerda
            lado = (x - c) * 0.5 + (y - c) * 0.85
            tom = sombra if lado > 3 else luz if lado < -3.4 else cor
            p[x, y] = tom + (255,)
    for x, y in ((5, 3), (6, 3), (4, 4), (5, 4), (3, 5)):  # brilho
        p[x, y] = (255, 255, 255, 255)
    return img


def main():
    sheet = Image.new("RGBA", (S * len(CORES), S))
    for i, cores in enumerate(CORES):
        sheet.paste(bolinha(*cores), (i * S, 0))
    sheet.save(OUT, optimize=True)
    print(OUT.relative_to(ROOT), sheet.size)


if __name__ == "__main__":
    main()
