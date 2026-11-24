import Phaser from 'phaser';
import BootScene from './scenes/BootScene.js';
import GameScene from './scenes/GameScene.js';
import UIScene from './scenes/UIScene.js';

// O canvas usa a resolucao real da tela (pixels fisicos) e o CSS reduz para o tamanho visual.
// Assim o zoom da camera pode ser um numero inteiro de pixels fisicos e cada pixel da arte
// fica exatamente do mesmo tamanho, sem distorcer nem tremer.
const dpr = () => Math.min(window.devicePixelRatio || 1, 4);
const cssSize = () => ({ w: window.innerWidth, h: window.innerHeight });

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
    arcade: { gravity: { y: 900 }, debug: false },
  },
  scene: [BootScene, GameScene, UIScene],
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

// facilita testes no console do navegador
window.__game = game;
