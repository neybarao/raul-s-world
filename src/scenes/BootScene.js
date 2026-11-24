import Phaser from 'phaser';
import { TILE } from '../config.js';
import { LEVELS, ENEMIES } from '../levels/index.js';

// ?v= muda a cada build, entao o navegador sempre baixa a versao nova das imagens
const asset = (path) => `assets/${path}?v=${__BUILD_ID__}`;

export default class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    const { width, height } = this.scale.gameSize;
    const bar = this.add.rectangle(width / 2 - 80, height / 2, 0, 6, 0xffd23f).setOrigin(0, 0.5);
    this.load.on('progress', (p) => (bar.width = 160 * p));

    this.load.spritesheet('raul', asset('sprites/raul.png'), { frameWidth: 64, frameHeight: 88 });
    this.load.spritesheet('dog', asset('sprites/dog.png'), { frameWidth: 52, frameHeight: 40 });
    this.load.spritesheet('enemy', asset('enemy.png'), { frameWidth: 32, frameHeight: 28 });
    this.load.spritesheet('hearts', asset('hearts.png'), { frameWidth: 18, frameHeight: 16 });
    this.load.image('raul-face', asset('sprites/raul-face.png'));
    this.load.image('coin', asset('sprites/coin.png'));
    this.load.spritesheet('mamae', asset('sprites/mamae.png'), { frameWidth: 88, frameHeight: 112 });
    this.load.image('tiles', asset('tiles.png'));
    // fases novas: chao, fundo, mola e inimigo de cada uma
    for (const lv of LEVELS) {
      if (lv.tiles !== 'tiles') this.load.image(lv.tiles, asset(`${lv.tiles}.png`));
      if (lv.bg) this.load.image(lv.bg, asset(`bg/${lv.id}.png`));
      this.load.image(`thumb-${lv.id}`, asset(`thumbs/${lv.id}.png`));
      this.load.spritesheet(lv.mola, asset(`${lv.mola}.png`), { frameWidth: 32, frameHeight: 24 });
    }
    for (const en of Object.values(ENEMIES)) {
      if (en.key !== 'enemy') this.load.spritesheet(en.key, asset(`${en.key}.png`), { frameWidth: en.frame[0], frameHeight: en.frame[1] });
    }
    this.load.image('cloud', asset('cloud.png'));
    this.load.image('hills-far', asset('hills-far.png'));
    this.load.image('trees-near', asset('trees-near.png'));
  }

  create() {
    const a = this.anims;
    const f = (key, frames) => frames.map((frame) => ({ key, frame }));
    a.create({ key: 'raul-idle', frames: f('raul', [0]) });
    a.create({ key: 'raul-run', frames: f('raul', [1, 2, 3, 4, 5, 6, 7, 8]), frameRate: 14, repeat: -1 });
    a.create({ key: 'raul-jump', frames: f('raul', [9]) });
    a.create({ key: 'raul-fall', frames: f('raul', [9]) });
    a.create({ key: 'raul-hurt', frames: f('raul', [10]) });
    a.create({ key: 'raul-cry', frames: f('raul', [11, 12]), frameRate: 3, repeat: -1 });
    a.create({ key: 'mamae-wait', frames: f('mamae', [0, 1]), frameRate: 2, repeat: -1 });
    a.create({ key: 'mamae-hug', frames: f('mamae', [2]) });
    a.create({ key: 'mamae-hug-love', frames: f('mamae', [3]) });
    a.create({ key: 'dog-run', frames: f('dog', [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]), frameRate: 20, repeat: -1 });
    a.create({ key: 'dog-stand', frames: f('dog', [0]) });
    a.create({ key: 'dog-sit', frames: f('dog', [1]) });
    a.create({ key: 'dog-sleep', frames: f('dog', [2]) });
    for (const en of Object.values(ENEMIES)) {
      a.create({ key: `${en.key}-walk`, frames: a.generateFrameNumbers(en.key, { frames: [0, 1] }), frameRate: 5, repeat: -1 });
    }

    this.registry.set('tile', TILE);
    this.scene.start('Menu');
    this.scene.launch('UI');
  }
}
