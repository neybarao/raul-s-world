"""Confere se todas as fases podem ser completadas, simulando a fisica do jogo.

Uso: python3 tools/check_levels.py
Para ser jogavel por criancas e idosos, a conta usa folga: o Raul so ANDANDO (sem correr) e com
o pulo mais fraco que o real (PULO_FOLGA). Se o fim de uma fase so for alcancavel no limite, o
verificador acusa. Inimigos nao entram na conta (da para pisar neles ou esperar).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = 32           # bloco em px
U = 2
GRAVITY = 900 * U
WALK = 105 * U
JUMP = 335 * U
MOLA = 1.45      # forca da mola em relacao ao pulo
MAX_FALL = 520 * U
PULO_FOLGA = 0.9  # ~10% menos altura que o pulo real
BODY_W, BODY_H = 20, 48
DT = 1 / 60


def load(name):
    src = (ROOT / f"src/levels/{name}.js").read_text()
    return re.findall(r"^  '(.*)',$", src, re.M)


class Sim:
    def __init__(self, rows):
        self.rows = rows
        self.w, self.h = len(rows[0]), len(rows)

    def cell(self, cx, cy):
        if cx < 0 or cx >= self.w:
            return "#"  # paredes nas pontas da fase
        if cy < 0 or cy >= self.h:
            return " "
        return self.rows[cy][cx]

    def solid(self, cx, cy):
        return self.cell(cx, cy) == "#"

    def jump(self, x, y, vx, vy):
        """Simula um salto a partir dos pes em (x, y). Devolve onde os pes param (ou None se cair)."""
        for _ in range(int(3 / DT)):
            vy = min(vy + GRAVITY * DT, MAX_FALL)
            nx = x + vx * DT
            # parede
            left, right = nx - BODY_W / 2, nx + BODY_W / 2
            hit_wall = False
            for cy in range(int((y - BODY_H + 1) // T), int((y - 1) // T) + 1):
                if self.solid(int(left // T), cy) or self.solid(int(right // T), cy):
                    hit_wall = True
            if not hit_wall:
                x = nx
            ny = y + vy * DT
            if vy < 0:  # subindo: teto
                head = ny - BODY_H
                if any(self.solid(int(px // T), int(head // T)) for px in (x - BODY_W / 2 + 1, x + BODY_W / 2 - 1)):
                    vy = 0
                    continue
                y = ny
                continue
            # caindo: chao (solido ou plataforma) cruzando a borda de cima de um bloco
            landed = None
            for px in (x - BODY_W / 2 + 1, x + BODY_W / 2 - 1):
                cx = int(px // T)
                top_row = int(y // T) if y % T else int(y // T)
                for cy in range(int(y // T), int(ny // T) + 1):
                    c = self.cell(cx, cy)
                    edge = cy * T
                    if c in "#=" and y <= edge <= ny:
                        landed = edge if landed is None else min(landed, edge)
            if landed is not None:
                # mola em cima desse chao?
                for px in (x - 8, x + 8):
                    if self.cell(int(px // T), int(landed // T) - 1) == "T":
                        return ("mola", x, landed)
                return ("chao", x, landed)
            y = ny
            if y > self.h * T + 200:
                return None
        return None

    def standable(self):
        """Pontos onde da para ficar parado: centro de cada bloco com chao embaixo e espaco em cima."""
        pts = []
        for cy in range(1, self.h):
            for cx in range(self.w):
                if self.cell(cx, cy) in "#=" and self.cell(cx, cy - 1) not in "#=":
                    pts.append((cx, cy))
        return pts


def check(name):
    rows = load(name)
    sim = Sim(rows)
    start = next((x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "P")
    flag = next((x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "F")
    surfaces = set(sim.standable())

    def surface_at(px, feet_y):
        return (int(px // T), int(feet_y // T))

    cache = {}

    def jump_from(sx, feet, vx, vy0):
        key = (sx, feet, vx, vy0)
        if key not in cache:
            res = sim.jump(sx, feet, vx, vy0)
            hops = 0
            while res and res[0] == "mola" and hops < 4:
                res = sim.jump(res[1], res[2], vx, -JUMP * PULO_FOLGA * MOLA)
                hops += 1
            cache[key] = res
        return cache[key]

    begin = (start[0], start[1] + 1)
    seen = {begin}
    todo = [begin]
    while todo:
        cx, cy = todo.pop()
        feet = cy * T
        nexts = []
        # andar para os lados no mesmo chao continuo
        for d in (-1, 1):
            nx = cx + d
            if (nx, cy) in surfaces and not sim.solid(nx, cy - 1):
                nexts.append((nx, cy))
        # pular (e cair da beira) para os dois lados, com velocidades variadas
        # do meio do bloco e da beirada (como uma pessoa faz antes de pular um buraco)
        for start_x in (cx * T + 2, cx * T + T / 2, cx * T + T - 2):
            for vx in (-WALK, 0, WALK):
                for vy0 in (-JUMP * PULO_FOLGA, 0.0):
                    res = jump_from(start_x, feet, vx, vy0)
                    if res:
                        nexts.append(surface_at(res[1], res[2]))
        for n in nexts:
            if n in surfaces and n not in seen:
                seen.add(n)
                todo.append(n)
    goal = (flag[0], flag[1] + 1)
    ok = goal in seen
    reach_x = max(x for x, _ in seen)
    return ok, reach_x


if __name__ == "__main__":
    names = sys.argv[1:] or [p.stem for p in sorted((ROOT / "src/levels").glob("*.js")) if p.stem != "index"]
    bad = 0
    for n in names:
        ok, rx = check(n)
        print(f"{'OK ' if ok else 'IMPOSSIVEL'} {n:10s} (mais longe que da para chegar: coluna {rx})")
        bad += not ok
    sys.exit(1 if bad else 0)
