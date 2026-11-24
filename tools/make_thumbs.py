"""Miniaturas das fases para o seletor (public/assets/thumbs/<fase>.png, 384x216).

Uso: python3 tools/make_thumbs.py  (rode depois de make_tiles.py e make_backgrounds.py)
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "public/assets"
OUT = A / "thumbs"
TW, TH = 384, 216  # mesma resolucao da arte (o carrossel mostra a miniatura grande)


def ground_strip(tiles_png, width):
    """Faixa de chao com o tile de topo e o de terra (tiles extrudados: margem 1, espaco 2)."""
    t = Image.open(tiles_png).convert("RGBA")
    top, body = t.crop((1, 1, 33, 33)), t.crop((35, 1, 67, 33))
    strip = Image.new("RGBA", (width, 64))
    for x in range(0, width, 32):
        strip.paste(top, (x, 0))
        strip.paste(body, (x, 32))
    return strip


def make(level, bg, tiles):
    canvas = Image.new("RGBA", (384, 216), (90, 168, 232, 255))
    if bg:
        img = Image.open(A / "bg" / f"{level}.png").convert("RGBA")
        img = img.crop((0, 0, 512, 341)).resize((384, 256), Image.NEAREST)
        canvas.alpha_composite(img, (0, 216 - 256 + 30))
    else:
        hills = Image.open(A / "hills-far.png")
        trees = Image.open(A / "trees-near.png")
        canvas.alpha_composite(hills.crop((0, 0, 384, 192)), (0, 216 - 192 - 30))
        canvas.alpha_composite(trees.crop((0, 0, 384, 192)), (0, 216 - 192 - 20))
        cloud = Image.open(A / "cloud.png")
        canvas.alpha_composite(cloud, (40, 20))
        canvas.alpha_composite(cloud, (250, 40))
    canvas.alpha_composite(ground_strip(A / f"{tiles}.png", 384), (0, 216 - 48))
    raul = Image.open(A / "sprites/raul.png").crop((0, 0, 64, 88))
    dog = Image.open(A / "sprites/dog.png").crop((0, 0, 52, 40))
    canvas.alpha_composite(raul, (150, 216 - 48 - 88))
    canvas.alpha_composite(dog, (92, 216 - 48 - 40))
    canvas.resize((TW, TH), Image.NEAREST).save(OUT / f"{level}.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make("floresta", True, "tiles")
    for lv in ("aquario", "bolinhas", "parque", "praia", "quartel", "escolinha", "italia"):
        make(lv, True, f"tiles-{lv}")
    print("ok")
