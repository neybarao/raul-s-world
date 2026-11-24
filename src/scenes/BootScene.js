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
    this.load.spritesheet('raul', 'sprites/raul.png', { frameWidth: 26, frameHeight: 34 });
    this.load.spritesheet('dog', 'sprites/dog.png', { frameWidth: 24, frameHeight: 20 });
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
    a.create({ key: 'raul-idle', frames: [{ key: 'raul', frame: 0 }] });
    a.create({ key: 'raul-run', frames: a.generateFrameNumbers('raul', { frames: [1, 2] }), frameRate: 8, repeat: -1 });
    a.create({ key: 'raul-jump', frames: [{ key: 'raul', frame: 3 }] });
    a.create({ key: 'dog-run', frames: a.generateFrameNumbers('dog', { frames: [0, 1] }), frameRate: 8, repeat: -1 });
    a.create({ key: 'dog-stand', frames: [{ key: 'dog', frame: 0 }] });
    a.create({ key: 'dog-sit', frames: [{ key: 'dog', frame: 2 }] });
    a.create({ key: 'dog-sleep', frames: [{ key: 'dog', frame: 3 }] });
    a.create({ key: 'enemy-walk', frames: a.generateFrameNumbers('enemy', { frames: [0, 1] }), frameRate: 5, repeat: -1 });

    this.registry.set('tile', TILE);
    this.scene.start('Game');
    this.scene.launch('UI');
  }
}
