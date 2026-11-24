# Raul's World

Jogo de plataforma 2D em pixel art com as aventuras do Raul (e do cachorro que vai atrás dele).
Roda no navegador: em pé no celular (com botões na faixa de baixo) e deitado no computador (teclado).

Jogar: https://neybarao.github.io/raul-s-world/

## Fases
No fim de cada fase o Raul corre para o colo da mamãe (agachada de braços abertos), que o pega,
gira e abraça. A mamãe foi desenhada no Magnific a partir de uma descrição.

Antes de jogar aparece o seletor de fases (toque no cartão duas vezes, ou direcional + A, ou setas + Enter):

| Fase | Desafio |
|---|---|
| Floresta | a fase original, com besouros (fundo no estilo da primeira arte do jogo) |
| Aquário | águas-vivas flutuando sobre os buracos |
| Piscina de Bolinhas | bolinhas bravas quicando e muitas molas |
| Parque Aquático | piscinas largas: boias e plataformas flutuantes |
| Praia | caranguejos e píer de madeira sobre o mar |
| Quartel da Mamãe | capivaras no gramado, caixotes em escada e pneus de mola |
| Escolinha | aviõezinhos de papel voando pela sala e pilhas de livros |

Os fundos das fases novas foram gerados no Magnific (GPT 2.6) em pixel art 32 bits, usando as
cores das fotos de férias da família (só as paletas foram enviadas, não as fotos). Os mapas ficam
em `tools/build_levels.py`; a lista de fases e o visual de cada uma em `src/levels/index.js`.
Legenda extra do mapa: `T` = mola. O recorde de moedas de cada fase fica guardado no aparelho.

## Controles
- Computador: setas ou A/D para andar, Espaço/W/↑ para pular, Shift ou X para correr, P ou Esc para pausar
- Celular: direcional em cruz para andar, A para pular, B (segurar) para correr, START para pausar

## App (PWA)
- **Android (Chrome):** menu ⋮ → "Instalar app" ou "Adicionar à tela inicial". Abre em tela cheia.
- **iPhone (Safari):** compartilhar → "Adicionar à Tela de Início". Abre sem barras do navegador
  (o iOS não permite tela cheia total; a área do relógio fica por cima do céu do jogo).
- **Atualizações:** cada publicação gera um `version.json` e um `sw.js` novos. O jogo confere a
  versão ao abrir, ao voltar para o app e a cada 5 minutos; se houver versão nova, mostra
  "Nova versão! Atualizando…" e recarrega sozinho.
- Ícones em `public/icons/`, gerados no Magnific com o modelo GPT 2.6 a partir do character sheet
  (original em `art/icon/icon-source.png`).

## Desenvolvimento
```bash
npm install
npm run dev      # abre em http://localhost:5173 (e na rede local, para testar no celular)
npm run build    # gera dist/
```
Cada push na `main` publica no GitHub Pages pelo workflow `.github/workflows/deploy.yml`.

## Estrutura
- `src/config.js`: números de jogabilidade (velocidade, pulo, dano, cachorro, zoom)
- `src/levels/*.js`: as fases desenhadas em texto (`#` chão, `=` plataforma, `o` moeda, `e` inimigo, `T` mola, `P` início, `F` bandeira), geradas por `tools/build_levels.py`
- `src/scenes/GameScene.js`: física, Raul, cachorro, inimigos, câmera
- `src/scenes/MenuScene.js`: seletor de fases
- `src/scenes/UIScene.js`: HUD, botões de toque, pausa e mensagens
- `public/assets/`: sprites e tiles
- `art/concept/`: imagens conceituais originais
- `tools/`: scripts Python que geram os sprites provisórios

## Arte
O Raul, o cachorro e o rosto do HUD saem direto do character sheet de referência
(`art/concept/character-sheet.png`) pelo `tools/pixelize_reference.py`: cada pose é recortada,
reduzida com a mesma escala, convertida para uma paleta única e ganha contorno de 1 pixel.
O ciclo de corrida (8 quadros) sai de um vídeo do Raul correndo no lugar, gerado no Magnific
(Seedance 2.0 Mini) a partir do character sheet; os quadros estão em `art/concept/run-cycle-video.jpg`.
Moeda e bandeira também. Tiles, inimigo, corações e fundo são
desenhados por código (`tools/make_tiles.py`).

| Arquivo | Quadros |
|---|---|
| `sprites/raul.png` | 13 quadros de 64×88 (parado, corrida 1 a 8, pulo, dano, choro 1, choro 2) |
| `sprites/dog.png` | 13 quadros de 52×40 (parado, sentado, dormindo, corrida 1 a 10) |
| `sprites/mamae.png` | 4 quadros de 88×112 (agachada 1 e 2, abraçando o Raul 1 e 2) |
| `enemy.png` | 3 quadros de 32×28 (andando 1, andando 2, amassado) |
| `tiles.png` | 9 tiles de 32×32, margem 1 e espaçamento 2 |
