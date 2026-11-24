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

## Arte
O Raul, o cachorro e o rosto do HUD saem direto do character sheet de referência
(`art/concept/character-sheet.png`) pelo `tools/pixelize_reference.py`: cada pose é recortada,
reduzida com a mesma escala, convertida para uma paleta única e ganha contorno de 1 pixel.
Moeda e bandeira vêm de `tools/extract_sprites.py`. Tiles, inimigo, corações e fundo são
desenhados por código (`tools/make_tiles.py`).

| Arquivo | Quadros |
|---|---|
| `sprites/raul.png` | 7 quadros de 32×44 (parado, corrida 1, corrida 2, pulo, dano, choro 1, choro 2) |
| `sprites/dog.png` | 4 quadros de 26×20 (andando, correndo, sentado, dormindo) |
| `enemy.png` | 3 quadros de 16×14 (andando 1, andando 2, amassado) |
| `tiles.png` | 9 tiles de 16×16, margem 1 e espaçamento 2 |
