// Lista de fases e o visual de cada uma. A ordem aqui e a ordem no seletor de fases.
import floresta from './floresta.js';
import aquario from './aquario.js';
import bolinhas from './bolinhas.js';
import parque from './parque.js';
import praia from './praia.js';
import quartel from './quartel.js';
import escolinha from './escolinha.js';

// faceRight: o desenho olha para a direita (os outros olham para a esquerda ou sao simetricos)
// tipos de inimigo:
//  walker  anda e vira na borda          floater  flutua subindo e descendo (nao cai)
//  bouncer quica pelo chao
export const ENEMIES = {
  besouro: { key: 'enemy', frame: [32, 28], body: [28, 22, 2, 6], kind: 'walker' },
  aguaviva: { key: 'enemy-aguaviva', frame: [32, 32], body: [22, 20, 5, 4], kind: 'floater', amp: [28, 26] },
  bola: { key: 'enemy-bola', frame: [32, 32], body: [22, 22, 5, 9], kind: 'bouncer' },
  patinho: { key: 'enemy-patinho', frame: [32, 32], body: [24, 24, 4, 7], kind: 'walker', faceRight: true },
  caranguejo: { key: 'enemy-caranguejo', frame: [32, 32], body: [24, 16, 4, 15], kind: 'walker' },
  capivara: { key: 'enemy-capivara', frame: [32, 32], body: [26, 18, 3, 12], kind: 'walker', faceRight: true },
  aviao: { key: 'enemy-aviao', frame: [32, 32], body: [24, 12, 4, 10], kind: 'floater', amp: [72, 12], faceRight: true },
};

export const LEVELS = [
  {
    id: 'floresta', name: 'Floresta', map: floresta, enemy: 'besouro',
    music: 'musica-ar-livre',
    sky: '#0379f7', tiles: 'tiles', mola: 'mola-floresta', bg: 'bg-floresta',
  },
  {
    id: 'aquario', name: 'Aquário', map: aquario, enemy: 'aguaviva',
    music: 'musica-ar-livre',
    sky: '#4fa8ad', tiles: 'tiles-aquario', mola: 'mola-aquario', bg: 'bg-aquario',
    water: 0x2e7f8c, bubbles: true,
  },
  {
    id: 'bolinhas', name: 'Piscina de Bolinhas', map: bolinhas, enemy: 'bola',
    music: 'musica-ar-livre',
    sky: '#777259', tiles: 'tiles-bolinhas', mola: 'mola-bolinhas', bg: 'bg-bolinhas',
  },
  {
    id: 'parque', name: 'Parque Aquático', map: parque, enemy: 'patinho',
    music: 'musica-ar-livre',
    sky: '#5e95d1', tiles: 'tiles-parque', mola: 'mola-parque', bg: 'bg-parque',
    water: 0x6cc8e4,
  },
  {
    id: 'praia', name: 'Praia', map: praia, enemy: 'caranguejo',
    music: 'musica-ar-livre',
    sky: '#5089e5', tiles: 'tiles-praia', mola: 'mola-praia', bg: 'bg-praia',
    water: 0x3aa8c0,
  },
  {
    id: 'quartel', name: 'Quartel da Mamãe', map: quartel, enemy: 'capivara',
    music: 'musica-quartel',
    sky: '#96b9bf', tiles: 'tiles-quartel', mola: 'mola-quartel', bg: 'bg-quartel',
  },
  {
    id: 'escolinha', name: 'Escolinha', map: escolinha, enemy: 'aviao',
    music: 'musica-ar-livre',
    sky: '#978a66', tiles: 'tiles-escolinha', mola: 'mola-escolinha', bg: 'bg-escolinha',
  },
];

export const levelById = (id) => LEVELS.find((l) => l.id === id) || LEVELS[0];
