"""Gera os mapas das fases em src/levels/*.js.

Uso: python3 tools/build_levels.py
Cada fase e desenhada por trechos. Legenda do mapa:
#  chao        =  plataforma (atravessa por baixo)     T  mola (pula bem alto)
o  moeda       e  inimigo da fase                      P  inicio   F  bandeira
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H, G = 112, 24, 21  # largura, altura, linha do topo do chao


class Level:
    def __init__(self):
        self.g = [[" "] * W for _ in range(H)]

    def ground(self, x0, x1, top=G):
        for x in range(x0, x1 + 1):
            for y in range(top, H):
                self.g[y][x] = "#"

    def plat(self, x0, x1, y):
        for x in range(x0, x1 + 1):
            self.g[y][x] = "="

    def put(self, x, y, c):
        self.g[y][x] = c

    def coins(self, xs, y):
        for x in xs:
            self.put(x, y, "o")

    def arc(self, x0, y0, n=5):
        """Arco de moedas (para pegar pulando)."""
        for i in range(n):
            h = [0, 1, 2, 1, 0][i * 4 // max(1, n - 1)] if n > 1 else 0
            self.put(x0 + i, y0 - h, "o")

    def save(self, name, title):
        rows = ["".join(r) for r in self.g]
        assert sum(r.count("P") for r in rows) == 1 and sum(r.count("F") for r in rows) == 1, name
        js = f"// {title}. Gerado por tools/build_levels.py (edite la e rode de novo).\n"
        js += "export default [\n" + "\n".join(f"  '{r}'," for r in rows) + "\n];\n"
        (ROOT / f"src/levels/{name}.js").write_text(js)
        print(name)
        print("\n".join(rows[9:]))


def aquario():
    """Aguas-vivas flutuando sobre os buracos: tem que esperar a hora certa de pular."""
    L = Level()
    L.ground(0, 19); L.put(3, G - 1, "P")
    L.coins(range(7, 11), G - 2)
    L.put(14, G - 1, "T"); L.arc(13, G - 7)
    # buraco com agua-viva no meio
    L.put(21, G - 3, "e"); L.coins([20, 21, 22], G - 6)
    L.ground(23, 40)
    L.plat(28, 31, 17); L.coins(range(28, 32), 16)
    L.put(35, G - 1, "e")  # agua-viva baixa no chao
    L.put(42, G - 4, "e")
    L.ground(44, 52, 19)
    L.put(50, 18, "T"); L.arc(48, 10)
    L.plat(55, 57, 15); L.put(59, 13, "e"); L.plat(61, 63, 13); L.coins(range(61, 64), 12)
    L.ground(66, 80)
    L.put(70, G - 3, "e"); L.coins(range(72, 78), G - 2)
    L.put(83, G - 4, "e")
    L.plat(82, 84, 19)
    L.ground(87, 111)
    L.put(92, G - 2, "e"); L.coins(range(95, 100), G - 2)
    L.put(104, G - 1, "F")
    L.save("aquario", "Aquario")


def bolinhas():
    """Muitas molas e bolinhas bravas quicando."""
    L = Level()
    L.ground(0, 22); L.put(3, G - 1, "P")
    L.put(9, G - 1, "T"); L.arc(8, G - 8)
    L.put(15, G - 1, "e"); L.coins(range(17, 21), G - 2)
    L.ground(25, 40)
    L.plat(27, 29, 17); L.plat(31, 33, 14); L.plat(35, 37, 11); L.coins(range(35, 38), 10)
    L.put(39, G - 1, "e")
    L.ground(43, 47); L.put(46, G - 1, "T")
    L.plat(50, 54, 15); L.coins(range(50, 55), 14)
    L.ground(57, 74)
    L.put(61, G - 1, "e"); L.put(67, G - 1, "e"); L.put(71, G - 1, "T"); L.arc(70, G - 8)
    L.ground(78, 84, 19); L.put(82, 18, "e")
    L.ground(85, 111)
    L.put(88, G - 1, "T"); L.plat(90, 94, 12); L.coins(range(90, 95), 11)
    L.put(97, G - 1, "e"); L.coins(range(99, 103), G - 2)
    L.put(106, G - 1, "F")
    L.save("bolinhas", "Piscina de bolinhas")


def parque():
    """Piscinas largas: boias (molas) e plataformas flutuantes para atravessar."""
    L = Level()
    L.ground(0, 20); L.put(3, G - 1, "P")
    L.put(12, G - 1, "e"); L.coins(range(8, 12), G - 2)
    L.put(19, G - 1, "T")
    # piscina larga com plataformas boiando
    L.plat(23, 25, 17); L.coins(range(23, 26), 16)
    L.plat(28, 30, 15); L.plat(33, 35, 17)
    L.ground(38, 54)
    L.put(43, G - 1, "e"); L.put(49, G - 1, "e")
    L.plat(44, 47, 17); L.coins(range(44, 48), 16)
    L.put(53, G - 1, "T"); L.arc(55, 9)
    L.plat(57, 60, 15); L.plat(63, 66, 16)
    L.ground(69, 84, 19)
    L.put(73, 18, "e"); L.coins(range(75, 80), 17); L.put(83, 18, "T")
    L.plat(86, 88, 14); L.plat(91, 93, 16)
    L.ground(96, 111)
    L.put(100, G - 1, "e")
    L.put(106, G - 1, "F")
    L.save("parque", "Parque aquatico")


def praia():
    """Caranguejos na areia e pier de madeira sobre o mar."""
    L = Level()
    L.ground(0, 26); L.put(3, G - 1, "P")
    L.put(11, G - 1, "e"); L.put(18, G - 1, "e"); L.coins(range(13, 17), G - 2)
    L.put(24, G - 1, "T"); L.arc(23, G - 8)
    L.plat(29, 37, 17); L.put(33, 16, "e"); L.coins([30, 31, 35, 36], 15)
    L.ground(40, 58)
    L.put(45, G - 1, "e"); L.put(51, G - 1, "e"); L.put(55, G - 1, "e")
    L.plat(47, 50, 17); L.coins(range(47, 51), 16)
    L.plat(61, 64, 19); L.plat(67, 70, 17); L.coins(range(67, 71), 16)
    L.ground(73, 80, 19); L.put(77, 18, "e")
    L.ground(81, 111)
    L.put(85, G - 1, "T"); L.plat(87, 92, 12); L.coins(range(87, 93), 11)
    L.put(96, G - 1, "e"); L.put(100, G - 1, "e")
    L.put(106, G - 1, "F")
    L.save("praia", "Praia")


def quartel():
    """Tatus correndo pelo gramado, caixotes empilhados e pneus de mola."""
    L = Level()
    L.ground(0, 24); L.put(3, G - 1, "P")
    L.put(10, G - 1, "e"); L.coins(range(12, 16), G - 2); L.put(19, G - 1, "e")
    L.plat(16, 18, 18); L.plat(20, 22, 15); L.coins(range(20, 23), 14)
    L.ground(28, 44)
    L.put(31, G - 1, "T"); L.arc(30, G - 8)
    L.ground(35, 37, 19); L.ground(38, 40, 17)  # caixotes em escada (como chao)
    L.coins([38, 39, 40], 15); L.put(43, G - 1, "e")
    L.plat(47, 50, 19); L.put(49, 18, "e")
    L.ground(53, 70)
    L.put(56, G - 1, "e"); L.put(62, G - 1, "e"); L.put(67, G - 1, "e")
    L.plat(58, 61, 17); L.coins(range(58, 62), 16)
    L.put(69, G - 1, "T"); L.plat(71, 74, 15); L.coins(range(71, 75), 14)
    L.ground(77, 84, 19); L.put(80, 18, "e")
    L.ground(87, 111)
    L.put(91, G - 1, "e"); L.coins(range(93, 98), G - 2); L.put(100, G - 1, "e")
    L.put(106, G - 1, "F")
    L.save("quartel", "Quartel")


def escolinha():
    """Avioezinhos de papel voando pela sala e pilhas de livros para subir."""
    L = Level()
    L.ground(0, 111); L.put(3, G - 1, "P")
    L.put(12, G - 4, "e"); L.coins(range(8, 12), G - 2)
    L.plat(15, 17, 18); L.plat(19, 21, 15); L.plat(23, 25, 12); L.coins(range(23, 26), 11)
    L.put(29, G - 3, "e"); L.put(33, G - 1, "T"); L.arc(32, G - 8)
    L.ground(37, 39, 19); L.ground(40, 42, 17); L.ground(43, 45, 15)  # degraus da escada
    L.coins([43, 44, 45], 13); L.put(48, G - 5, "e")
    L.plat(51, 54, 17); L.put(57, G - 3, "e"); L.coins(range(51, 55), 16)
    L.put(61, G - 1, "T"); L.plat(63, 67, 11); L.coins(range(63, 68), 10); L.put(70, 9, "e")
    L.plat(72, 75, 15); L.put(78, G - 4, "e")
    L.ground(81, 86, 19); L.coins(range(81, 87), 17)
    L.put(90, G - 3, "e"); L.put(96, G - 5, "e"); L.coins(range(92, 100, 2), G - 2)
    L.put(106, G - 1, "F")
    L.save("escolinha", "Escolinha")


def italia():
    """Toscana: morros em degraus, pombos de praca e telhados de terracota sobre os buracos."""
    L = Level()
    L.ground(0, 22); L.put(3, G - 1, "P")
    L.coins(range(8, 12), G - 2); L.put(13, G - 1, "e"); L.put(19, G - 1, "e")
    # primeiro morro: sobe em dois degraus e desce
    L.ground(23, 30, 19); L.ground(31, 36, 17); L.coins(range(31, 37), 15); L.put(34, 16, "e")
    L.ground(37, 42, 19)
    # telhado sobre o buraco
    L.plat(44, 46, 18); L.coins([44, 45, 46], 16)
    L.ground(48, 62)
    L.put(51, G - 1, "e"); L.put(56, G - 1, "T"); L.arc(55, G - 8)
    L.plat(58, 61, 15); L.coins(range(58, 62), 14)
    L.ground(63, 68, 19); L.put(66, 18, "e")
    # vinhedo no alto do morro
    L.ground(72, 78, 18); L.coins(range(73, 78), 16)
    L.ground(79, 84, 16); L.put(82, 15, "e"); L.coins([80, 81, 83], 14)
    L.ground(85, 111)
    L.put(90, G - 1, "e"); L.plat(93, 97, 17); L.coins(range(93, 98), 16)
    L.put(100, G - 1, "e"); L.coins(range(101, 104), G - 2)
    L.put(106, G - 1, "F")
    L.save("italia", "Italia")


if __name__ == "__main__":
    italia()
    quartel()
    escolinha()
    aquario()
    bolinhas()
    parque()
    praia()
