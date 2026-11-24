import Phaser from 'phaser';
import BootScene from './scenes/BootScene.js';
import GameScene from './scenes/GameScene.js';
import UIScene from './scenes/UIScene.js';
import MenuScene from './scenes/MenuScene.js';
import { GRAVITY } from './config.js';
import { setupPWA, setupFullscreen } from './pwa.js';
import { musicState } from './music.js';

// O canvas usa a resolucao real da tela (pixels fisicos) e o CSS reduz para o tamanho visual.
// Assim o zoom da camera pode ser um numero inteiro de pixels fisicos e cada pixel da arte
// fica exatamente do mesmo tamanho, sem distorcer nem tremer.
const dpr = () => Math.min(window.devicePixelRatio || 1, 4);
// No iPhone, com o jogo instalado na tela de inicio (barra de status transparente), o
// window.innerHeight vem menor que a tela (desconta a barra de status) e sobrava uma faixa vazia
// embaixo. Como app, mede a altura por um elemento de 100vh, que ocupa a tela inteira.
const standalone = () =>
  window.navigator.standalone === true ||
  window.matchMedia('(display-mode: standalone)').matches ||
  window.matchMedia('(display-mode: fullscreen)').matches;
const probe = document.createElement('div');
probe.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:100vh;visibility:hidden;pointer-events:none';
document.body.appendChild(probe);
const cssSize = () => {
  const h = standalone() ? Math.max(window.innerHeight, probe.offsetHeight) : window.innerHeight;
  return { w: window.innerWidth, h };
};

const { w, h } = cssSize();
const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  backgroundColor: '#1b1b2a',
  pixelArt: true,
  roundPixels: true,
  scale: {
    mode: Phaser.Scale.NONE,
    width: Math.round(w * dpr()),
    height: Math.round(h * dpr()),
  },
  input: { activePointers: 4 },
  physics: {
    default: 'arcade',
    arcade: { gravity: { y: GRAVITY }, debug: false },
  },
  scene: [BootScene, MenuScene, GameScene, UIScene],
});

function fit() {
  const { w, h } = cssSize();
  game.scale.resize(Math.round(w * dpr()), Math.round(h * dpr()));
  game.canvas.style.width = `${w}px`;
  game.canvas.style.height = `${h}px`;
  game.scale.refresh();
}
game.events.once('ready', fit);
window.addEventListener('resize', fit);
window.addEventListener('orientationchange', () => setTimeout(fit, 200));

setupPWA();
setupFullscreen();

// facilita testes no console do navegador
window.__game = game;
window.__build = __BUILD_ID__;
window.__music = musicState;
