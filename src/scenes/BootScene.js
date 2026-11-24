import Phaser from 'phaser';
import { TILE } from '../config.js';

export default class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    const { width, height } = this.scale.gameSize;
    const bar = this.add.rectangle(width / 2 - 80, height / 2, 0, 6, 0xffd23f).setOrigin(0, 0.5);
    this.load.on('progress', (p) => (bar.width = 160 * p));

    this.load.setPath('assets/');
    this.load.spritesheet('raul', 'sprites/raul.png', { frameWidth: 20, frameHeight: 26 });
    this.load.spritesheet('dog', 'sprites/dog.png', { frameWidth: 22, frameHeight: 16 });
    this.load.spritesheet('enemy', 'enemy.png', { frameWidth: 16, frameHeight: 14 });
    this.load.spritesheet('hearts', 'hearts.png', { frameWidth: 9, frameHeight: 8 });
    this.load.image('raul-face', 'sprites/raul-face.png');
    this.load.image('coin', 'sprites/coin.png');
    this.load.image('flag', 'sprites/flag.png');
    this.load.image('tiles', 'tiles.png');
    this.load.image('cloud', 'cloud.png');
    this.load.image('hills-far', 'hills-far.png');
    this.load.image('trees-near', 'trees-near.png');
  }

  create() {
    const a = this.anims;
    const f = (key, frames) => frames.map((frame) => ({ key, frame }));
    a.create({ key: 'raul-idle', frames: f('raul', [0, 0, 0, 0, 0, 0, 0, 1]), frameRate: 4, repeat: -1 });
    a.create({ key: 'raul-run', frames: f('raul', [2, 3, 4, 5]), frameRate: 10, repeat: -1 });
    a.create({ key: 'raul-jump', frames: f('raul', [6]) });
    a.create({ key: 'raul-fall', frames: f('raul', [7]) });
    a.create({ key: 'raul-hurt', frames: f('raul', [8]) });
    a.create({ key: 'dog-run', frames: f('dog', [0, 1]), frameRate: 9, repeat: -1 });
    a.create({ key: 'dog-stand', frames: f('dog', [2]) });
    a.create({ key: 'dog-sit', frames: f('dog', [3]) });
    a.create({ key: 'dog-sleep', frames: f('dog', [4]) });
    a.create({ key: 'enemy-walk', frames: a.generateFrameNumbers('enemy', { frames: [0, 1] }), frameRate: 5, repeat: -1 });

    this.registry.set('tile', TILE);
    this.scene.start('Game');
    this.scene.launch('UI');
  }
}
