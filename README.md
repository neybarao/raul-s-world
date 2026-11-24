# Raul's World

Jogo de plataforma 2D em pixel art com as aventuras do Raul (e do cachorro que vai atrás dele).
Roda no navegador: em pé no celular (com botões na faixa de baixo) e deitado no computador (teclado).

Jogar: https://neybarao.github.io/raul-s-world/

## Fases
No fim de cada fase o Raul corre para o colo da mamãe (agachada de braços abertos), que o pega,
gira e abraça. A mamãe foi desenhada no Magnific a partir de uma descrição.

Antes de jogar aparece o seletor de fases (toque no cartão duas vezes, ou direcional + A, ou setas + Enter).
No celular em pé as fases aparecem num carrossel (um cartão grande por vez: deslize o dedo ou use o
direcional; tocar no cartão do meio começa a fase); deitado, em grade de 4:

| Fase | Desafio |
|---|---|
| Floresta | a fase original, com besouros (fundo no estilo da primeira arte do jogo) |
| Aquário | águas-vivas flutuando sobre os buracos |
| Piscina de Bolinhas | bolinhas bravas quicando e muitas molas |
| Parque Aquático | piscinas largas: boias e plataformas flutuantes |
| Praia | caranguejos e píer de madeira sobre o mar |
| Quartel da Mamãe | capivaras no gramado, caixotes em escada e pneus de mola |
| Escolinha | aviõezinhos de papel voando pela sala e pilhas de livros |
| Itália | Toscana: morros em degraus, pombos de praça e telhados de terracota sobre os buracos |

Os fundos das fases novas foram gerados no Magnific (GPT 2.6) em pixel art 32 bits, usando as
cores das fotos de férias da família (só as paletas foram enviadas, não as fotos). Os mapas ficam
em `tools/build_levels.py`; a lista de fases e o visual de cada uma em `src/levels/index.js`.
Legenda extra do mapa: `T` = mola. O recorde de moedas de cada fase fica guardado no aparelho.

## Logo
"RAUL / AVENTUREIRO" no topo do seletor de fases. Gerada no Magnific (GPT 2.6) sobre fundo verde
(`art/concept/logo-source.jpg`) e convertida em pixel art de verdade por `tools/make_logo.py`
(tira o fundo, reduz pelo tamanho do pixel da arte e limita a paleta). Saída: `public/assets/logo.png`
(146×68), ampliada em escala inteira no menu.

## Música
Trilhas chiptune originais geradas no Magnific (Google Lyria 3), recortadas em compassos inteiros
para repetir sem emenda (originais em `art/music/`, versões do jogo em `public/assets/music/`):
- `menu.mp3`: seletor de fases
- `ar-livre.mp3`: fases em geral
- `quartel.mp3`: Quartel da Mamãe

A música de cada fase fica em `src/levels/index.js` (campo `music`). O botão de alto-falante (ou a
tecla M) liga e desliga o som, e a escolha fica guardada no aparelho. Na pausa o volume abaixa.

## Controles
- Computador: setas ou A/D para andar, Espaço/W/↑ para pular, X para arremessar bolinha (segurando, corre também), C só arremessa, Shift só corre, P ou Esc para pausar, M para ligar/desligar o som
- Celular: direcional em cruz para andar, A para pular, B para arremessar bolinha (segurando, o Raul também corre), START para pausar

## App (PWA)
- **Android (Chrome):** menu ⋮ → "Instalar app" ou "Adicionar à tela inicial". Abre em tela cheia.
- **iPhone (Safari):** compartilhar → "Adicionar à Tela de Início". Abre sem barras do navegador
  (o iOS não permite tela cheia total; a área do relógio fica por cima do céu do jogo).
- **Atualizações:** cada publicação gera um `version.json` e um `sw.js` novos. O jogo confere a
  versão ao abrir, ao voltar para o app e a cada 5 minutos; se houver versão nova, mostra
  "Nova versão! Atualizando…" e recarrega sozinho.
- **Offline:** na primeira visita o service worker baixa o jogo inteiro (código, imagens e músicas).
  Depois disso dá para jogar sem internet.
- Ícones em `public/icons/`, gerados no Magnific (GPT 2.6) a partir dos sprites do jogo
  (`art/icon/style-reference.png`); original em `art/icon/icon-source.png`.

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
- `tools/check_levels.py`: confere se todas as fases dá pra terminar só andando (sem correr) e com um pulo 10% mais fraco que o real. Rode `python3 tools/check_levels.py` depois de mexer em qualquer fase; ele avisa a coluna onde fica impossível.
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
A pose de arremesso (2 quadros) foi gerada no Magnific (GPT 2.6) a partir do character sheet
(`art/concept/throw-sheet.jpg`). A bolinha mira sozinha no bicho mais perto à frente.
O ciclo de corrida (8 quadros) sai de um vídeo do Raul correndo no lugar, gerado no Magnific
(Seedance 2.0 Mini) a partir do character sheet; os quadros estão em `art/concept/run-cycle-video.jpg`.
Moeda e bandeira também. Tiles, inimigo, corações e fundo são
desenhados por código (`tools/make_tiles.py`).

| Arquivo | Quadros |
|---|---|
| `sprites/raul.png` | 15 quadros de 64×88 (parado, corrida 1 a 8, pulo, dano, choro 1, choro 2, arremesso preparando, arremesso soltando) |
| `sprites/dog.png` | 13 quadros de 52×40 (parado, sentado, dormindo, corrida 1 a 10) |
| `sprites/mamae.png` | 4 quadros de 88×112 (agachada 1 e 2, abraçando o Raul 1 e 2) |
| `bolinhas.png` | 6 quadros de 18×18 (bolinhas de piscina arremessadas com o B; `tools/make_bolinhas.py`) |
| `enemy.png` | 3 quadros de 32×28 (andando 1, andando 2, amassado) |
| `tiles.png` | 9 tiles de 32×32, margem 1 e espaçamento 2 |
