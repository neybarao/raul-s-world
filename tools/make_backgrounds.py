"""Converte os fundos gerados no Magnific (GPT 2.6) em texturas de pixel art que repetem sem emenda.

Uso: python3 tools/make_backgrounds.py
Entrada: art/backgrounds/<fase>.jpg (panoramas 3:1). Saida: public/assets/bg/<fase>.png
Cada panorama vira paleta limitada e e espelhado (original + invertido), assim a borda direita
sempre encaixa na esquerda quando o fundo se repete.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art/backgrounds"
OUT = ROOT / "public/assets/bg"
COLORS = 64


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.glob("*.jpg")):
        img = Image.open(src).convert("RGB")
        # tira o ruido de JPEG antes de reduzir as cores
        q = img.quantize(colors=COLORS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
        mirrored = Image.new("RGB", (q.width * 2, q.height))
        mirrored.paste(q, (0, 0))
        mirrored.paste(q.transpose(Image.FLIP_LEFT_RIGHT), (q.width, 0))
        mirrored.save(OUT / f"{src.stem}.png", optimize=True)
        top = q.crop((0, 0, q.width, 6)).resize((1, 1), Image.BOX).getpixel((0, 0))
        print(src.stem, mirrored.size, "cor do topo #%02x%02x%02x" % top)


if __name__ == "__main__":
    main()
