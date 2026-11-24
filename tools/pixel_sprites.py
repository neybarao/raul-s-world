"""Sprites do Raul e do cachorro desenhados pixel a pixel.

Cada letra e um pixel com uma cor da paleta; '.' e transparente.
Para editar: mude as letras, rode `python3 tools/pixel_sprites.py` e recarregue o jogo.
Referencia: art/concept/character-sheet.png
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public/assets/sprites"

PAL = {
    "K": (58, 30, 20),     # contorno
    "H": (184, 86, 31),    # cabelo
    "h": (226, 128, 48),   # cabelo brilho
    "d": (122, 52, 18),    # cabelo sombra
    "S": (246, 192, 146),  # pele
    "s": (222, 150, 104),  # pele sombra
    "B": (244, 140, 130),  # bochecha
    "E": (40, 24, 16),     # olho
    "W": (255, 255, 255),  # brilho do olho / branco
    "M": (150, 40, 40),    # boca
    "m": (236, 96, 96),    # lingua
    "x": (214, 60, 54),    # marquinha na testa
    "R": (226, 58, 40),    # camiseta
    "r": (168, 36, 24),    # camiseta sombra
    "P": (216, 184, 132),  # bermuda
    "p": (168, 136, 90),   # bermuda sombra
    "F": (244, 244, 244),  # meia
    "N": (214, 40, 40),    # tenis
    "n": (250, 250, 250),  # sola
    # cachorro
    "O": (110, 92, 84),    # contorno do pelo
    "C": (252, 248, 238),  # pelo
    "c": (220, 210, 196),  # pelo sombra
    "L": (208, 40, 40),    # coleira
    "G": (246, 196, 46),   # plaquinha
    "T": (40, 30, 30),     # nariz e olho
    "t": (240, 120, 130),  # lingua do cachorro
}

# ---------------- RAUL (quadro 20x26, olhando para a direita) ----------------

HEAD = [  # 13 linhas
    ".....KKK.KKK.KK.....",
    "....KhHHKHhHKHHK....",
    "...KHhHHHhHHHhHHK...",
    "..KHHHdHHHHdHHHHHK..",
    "..KHdHHHHHHHHHdHHK..",
    ".KHHHHHHdHHHHHHHHHK.",
    ".KHHdHHHSxSSHHSHdHK.",
    ".KHHHHSSSSSSSSSSHK..",
    "..KHsHSSSSEWSSEWSK..",
    "..KHssSSSSEESSEESK..",
    "...KsSSSBSSSSSSSBK..",
    "...KKSSSSSSKMMKSK...",
    ".....KKSSSSSSSSKK...",
]

HEAD_BLINK = HEAD[:8] + [
    "..KHsHSSSSSSSSSSSK..",
    "..KHssSSSSEESSEESK..",
] + HEAD[10:]

HEAD_HAPPY = HEAD[:11] + [  # boca aberta, para pulo
    "...KKSSSSSSKMMMKSK..",
    ".....KKSSSSSKmmKK...",
]

HEAD_HURT = HEAD[:8] + [
    "..KHsHSSSSESSSSESK..",
    "..KHssSSSSSESSESSK..",
    "...KsSSSBSSSSSSSBK..",
    "...KKSSSSSSSKMKSK...",
    ".....KKSSSSSSSSKK...",
]

# corpos: 13 linhas (linhas 13 a 25 do quadro)
BODY_IDLE = [
    ".......KKKKKK.......",
    "......KRRRRRRK......",
    ".....KRRRRRRRRK.....",
    "....KSKRRRRRRKSK....",
    "....KSKRRRRRrKSK....",
    ".....KKRRRRRrKK.....",
    "......KPPPPPPK......",
    "......KPPPpPPK......",
    "......KPPKKPPK......",
    "......KSSKKSSK......",
    "......KFFK.KFFK.....",
    ".....KNNNK.KNNNK....",
    ".....KnnnK.KnnnnK...",
]

BODY_IDLE2 = BODY_IDLE[:1] + [  # respiracao: ombros 1px mais largos
    "......KRRRRRRK......",
    ".....KRRRRRRRRK.....",
    "....KSKRRRRRRKSK....",
    "....KSKRRRRRrKSK....",
    ".....KKRRRRRrKK.....",
] + BODY_IDLE[6:]

BODY_RUN_A = [  # perna da frente esticada, de tras levantada
    ".......KKKKKK.......",
    "......KRRRRRRKKK....",
    ".....KRRRRRRRRSSK...",
    "....KKRRRRRRRRKK....",
    "...KSKRRRRRrRK......",
    "...KKKRRRRRrK.......",
    "......KPPPPPPK......",
    "......KPPPpPPPK.....",
    ".....KPPPK.KPPSK....",
    "...KKSSK....KSSK....",
    ".KnNFFK......KFFK...",
    ".KKNNK......KNNNNK..",
    "..KKK.......KnnnnK..",
]

BODY_RUN_B = [  # passagem: joelho da frente levantado
    ".......KKKKKK.......",
    "......KRRRRRRK......",
    ".....KRRRRRRRRK.....",
    ".....KSRRRRRRRK.....",
    ".....KSKRRRRrK......",
    "......KKRRRRrK......",
    "......KPPPPPPKK.....",
    "......KPPpPPPPSK....",
    ".......KPPPKKSSK....",
    ".......KSSK.KFFK....",
    ".......KFFK.KNNNK...",
    "......KNNNK.KnnnK...",
    "......KnnnnK.KKK....",
]

BODY_RUN_C = [  # como A, com os bracos trocados
    ".......KKKKKK.......",
    ".....KKRRRRRRK......",
    "....KSSRRRRRRRK.....",
    ".....KKRRRRRRRKK....",
    ".......KRRRRrRKSK...",
    "........KRRRrKKKK...",
] + BODY_RUN_A[6:]

BODY_RUN = [BODY_RUN_A, BODY_RUN_B, BODY_RUN_C, BODY_RUN_B]

BODY_JUMP = [
    "...KK..KKKKKK..KK...",
    "...KSKKRRRRRRKKSK...",
    "....KSRRRRRRRRSK....",
    ".....KRRRRRRRRK.....",
    ".....KRRRRRRrRK.....",
    "......KRRRRRrK......",
    "......KPPPPPPK......",
    ".....KPPPpPPPPK.....",
    "....KSPPKKKPPSSK....",
    "...KFSSK...KKSSFK...",
    "..KNNFK......KFNNK..",
    "..KnNNK......KNNnK..",
    "...KKK........KKK...",
]

BODY_FALL = [
    ".......KKKKKK.......",
    "..KK..KRRRRRRK..KK..",
    "..KSKKRRRRRRRRKKSK..",
    "...KSSKRRRRRRKSSK...",
    "....KKKRRRRRrKKK....",
    "......KRRRRRrK......",
    "......KPPPPPPK......",
    "......KPPpPPPK......",
    "......KPPKKPPK......",
    ".....KSSK..KSSK.....",
    ".....KFFK..KFFK.....",
    "....KNNNK..KNNNK....",
    "....KnnnK..KnnnK....",
]


def raul_frames():
    def frame(head, body, bob=0):
        rows = ["." * 20] * bob + head + body
        rows = rows[: 26]
        while len(rows) < 26:
            rows = ["." * 20] + rows
        return rows

    return [
        frame(HEAD, BODY_IDLE),          # 0 parado
        frame(HEAD_BLINK, BODY_IDLE2),   # 1 parado piscando / respirando
        frame(HEAD, BODY_RUN[0]),        # 2 corrida
        frame(HEAD, BODY_RUN[1], 1),     # 3
        frame(HEAD, BODY_RUN[2]),        # 4
        frame(HEAD, BODY_RUN[3], 1),     # 5
        frame(HEAD_HAPPY, BODY_JUMP),    # 6 subindo
        frame(HEAD, BODY_FALL),          # 7 caindo
        frame(HEAD_HURT, BODY_FALL),     # 8 dano
    ]


# ---------------- CACHORRO (quadro 22x16, olhando para a direita) ----------------

DOG_HEAD = [  # 10 x 8, orelha caida a esquerda do rosto
    "...OOOO...",
    "..OCCcCOO.",
    ".OCCCCCCCO",
    "OcOCCCTCCO",
    "OccOCCCCCT",
    "OccOCCCCtO",
    ".OOLLLLOO.",
    "...OLGLO..",
]


def overlay(base, part, x0, y0):
    rows = [list(r) for r in base]
    for y, row in enumerate(part):
        for x, ch in enumerate(row):
            if ch != "." and 0 <= y0 + y < len(rows) and 0 <= x0 + x < len(rows[0]):
                rows[y0 + y][x0 + x] = ch
    return ["".join(r) for r in rows]


def dog(body, head_y=1, head_x=12):
    return overlay(body, DOG_HEAD, head_x, head_y)


DOG_STAND = dog([
    "......................",
    "......................",
    "...OO.................",
    "..OCcO................",
    "..OCCO................",
    "...OCO................",
    "...OCOOOOOOOO.........",
    "...OCCCCcCCCCCO.......",
    "..OCCCCCCCCCCCCO......",
    "..OCcCCCcCCCCCCO......",
    "..OCccCCCCCCCccO......",
    "...OCcOOOOOOOCcO......",
    "...OCCO.....OCCO......",
    "...OCCO.....OCCO......",
    "...OCCO.....OCCO......",
    "...OOOO.....OOOO......",
])

DOG_RUN1 = dog([
    "......................",
    "......................",
    "......................",
    "......................",
    ".OOO..................",
    "OCcCO.................",
    "OCCCOOOOOOOOO.........",
    ".OOCCCCcCCCCCCO.......",
    "...OCCCCCCCCCCCO......",
    "..OCcCCCcCCCCCCO......",
    "..OCccCCCCCCCcCOO.....",
    ".OCcOOOOOOOOOOOCCO....",
    "OCCO...........OCCO...",
    "OCO.............OCCO..",
    "OO...............OOO..",
    "......................",
], head_y=2)

DOG_RUN2 = dog([
    "......................",
    "......................",
    "......................",
    "...OO.................",
    "..OCcO................",
    "..OCCO................",
    "...OCO................",
    "...OCOOOOOOOO.........",
    "...OCCCCcCCCCCO.......",
    "..OCCCCCCCCCCCCO......",
    "..OCcCCCcCCCCCCO......",
    "..OCccCCCCCCCccO......",
    "...OCcOOOOOOOCcO......",
    "....OCCO...OCCO.......",
    "....OCCO...OCCO.......",
    "....OOOO...OOOO.......",
], head_y=2)

DOG_SIT = dog([
    "......................",
    "......................",
    "......................",
    "......................",
    "......................",
    "......................",
    "......................",
    "..OO.......OOOO.......",
    ".OCcO....OOCCCCO......",
    ".OCCO...OCCCCCCO......",
    "..OCOOOOCCCcCCCO......",
    "...OCCCCCCCCCCCO......",
    "...OCcCCCCCCCOCO......",
    "...OCccCCCCCOCCO......",
    "....OCCCCCCOCCCO......",
    ".....OOOOOOOOOOO......",
], head_y=2, head_x=10)

DOG_SLEEP = overlay([
    "......................",
    "......................",
    "......................",
    "......................",
    "......................",
    "......................",
    "......................",
    "......................",
    "..OO..................",
    ".OCcO.OOOOOOOOO.......",
    ".OCCOOCCCCcCCCCO......",
    "..OCCCCCCCCCCCCCO.....",
    "..OCcCCCcCCCCCCCCO....",
    "..OCccCCCCCCCCCcCO....",
    "...OOOOOOOOOOOOOOO....",
    "......................",
], [  # cabeca deitada, olho fechado
    "...OOOO...",
    "..OCCcCOO.",
    ".OCCCCCCCO",
    "OcOCCCOOCO",
    "OccOCCCCCT",
    "OccOLLLLCO",
    ".OOOOGOOO.",
], 12, 8)


def dog_frames():
    return [DOG_RUN1, DOG_RUN2, DOG_STAND, DOG_SIT, DOG_SLEEP]


def render(frames, fw, fh, name):
    img = Image.new("RGBA", (fw * len(frames), fh), (0, 0, 0, 0))
    for i, rows in enumerate(frames):
        assert len(rows) == fh, f"{name} quadro {i}: {len(rows)} linhas"
        for y, row in enumerate(rows):
            assert len(row) == fw, f"{name} quadro {i} linha {y}: {len(row)} colunas ({row!r})"
            for x, ch in enumerate(row):
                if ch != ".":
                    img.putpixel((i * fw + x, y), PAL[ch] + (255,))
    img.save(OUT / f"{name}.png")
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    render(raul_frames(), 20, 26, "raul")
    render(dog_frames(), 22, 16, "dog")
    print("ok")
