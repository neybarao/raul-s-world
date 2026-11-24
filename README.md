# Raul's World

Jogo de plataforma 2D em pixel art com as aventuras do Raul (e do cachorro que vai atrás dele).
Roda no navegador: em pé no celular (com botões na faixa de baixo) e deitado no computador (teclado).

Jogar: https://neybarao.github.io/raul-s-world/

## Controles
- Computador: setas ou A/D para andar, Espaço/W/↑ para pular, Shift ou X para correr, P ou Esc para pausar
- Celular: direcional em cruz para andar, A para pular, B (segurar) para correr, START para pausar

## Desenvolvimento
```bash
npm install
npm run dev      # abre em http://localhost:5173 (e na rede local, para testar no celular)
npm run build    # gera dist/
```
Cada push na `main` publica no GitHub Pages pelo workflow `.github/workflows/deploy.yml`.

## Estrutura
- `src/config.js`: números de jogabilidade (velocidade, pulo, dano, cachorro, zoom)
- `src/levels/level1.js`: a fase desenhada em texto (`#` chão, `=` plataforma, `o` moeda, `e` inimigo, `P` início, `F` bandeira)
- `src/scenes/GameScene.js`: física, Raul, cachorro, inimigos, câmera
- `src/scenes/UIScene.js`: HUD, botões de toque, pausa e mensagens
- `public/assets/`: sprites e tiles
- `art/concept/`: imagens conceituais originais
- `tools/`: scripts Python que geram os sprites provisórios

## Arte provisória
O Raul e o cachorro são desenhados pixel a pixel em `tools/pixel_sprites.py` (cada letra é um
pixel de uma paleta fixa). O rosto do HUD, a moeda e a bandeira ainda são recortes das imagens
conceituais (`tools/extract_sprites.py`). Tiles, inimigo, corações e fundo são desenhados por código
(`tools/make_tiles.py`). Tudo deve ser trocado pela arte final em grade de pixels real,
mantendo os mesmos tamanhos de quadro:

| Arquivo | Quadros |
|---|---|
| `sprites/raul.png` | 9 quadros de 20×26 (parado, piscando, corrida 1 a 4, subindo, caindo, dano) |
| `sprites/dog.png` | 5 quadros de 22×16 (correndo 1 e 2, parado, sentado, dormindo) |
| `enemy.png` | 3 quadros de 16×14 (andando 1, andando 2, amassado) |
| `tiles.png` | 9 tiles de 16×16, margem 1 e espaçamento 2 |
