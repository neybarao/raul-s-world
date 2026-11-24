import Phaser from 'phaser';
import { LEVELS } from '../levels/index.js';
import { touch, layout, computeLayout } from '../controls.js';

const FONT = { fontFamily: '"Courier New", monospace', fontStyle: 'bold', color: '#ffffff' };

// Seletor de fases: toque num cartao, ou use o direcional / setas e A / Enter.
export default class MenuScene extends Phaser.Scene {
  constructor() {
    super('Menu');
  }

  create() {
    this.registry.set('mode', 'menu');
    this.game.events.emit('mode', 'menu');
    const last = this.registry.get('level');
    this.selected = Math.max(0, LEVELS.findIndex((l) => l.id === last));
    // a cena e reaproveitada a cada volta ao menu: zera o estado da entrada anterior
    this.starting = false;
    this.cameras.main.resetFX();
    this.cameras.main.fadeIn(200, 27, 27, 42);
    // ignora o A que ainda estiver apertado (o toque que fechou a fase)
    this.prev = { left: touch.left, right: touch.right, jump: true };
    this.cards = [];

    this.bg = this.add.graphics();
    this.title = this.add.text(0, 0, "Raul's World", { ...FONT, color: '#ffd23f' }).setOrigin(0.5);
    this.subtitle = this.add.text(0, 0, 'Escolha a fase', FONT).setOrigin(0.5);
    this.raul = this.add.sprite(0, 0, 'raul', 0).setOrigin(0.5, 1).play('raul-run');
    this.dog = this.add.sprite(0, 0, 'dog', 0).setOrigin(0.5, 1).play('dog-run');

    LEVELS.forEach((lv, i) => {
      const card = this.add.container(0, 0);
      card.frame = this.add.graphics();
      card.thumb = this.add.image(0, 0, `thumb-${lv.id}`).setOrigin(0, 0);
      card.label = this.add.text(0, 0, lv.name, FONT).setOrigin(0.5, 0);
      card.best = this.add.text(0, 0, '', { ...FONT, color: '#ffd23f' }).setOrigin(0.5, 0);
      card.add([card.frame, card.thumb, card.label, card.best]);
      card.zone = this.add.zone(0, 0, 10, 10).setOrigin(0, 0).setInteractive();
      card.zone.on('pointerup', () => {
        if (this.selected === i) this.start(i);
        else this.select(i);
      });
      this.cards.push(card);
    });

    const kb = this.input.keyboard;
    kb.on('keydown-LEFT', () => this.move(-1));
    kb.on('keydown-RIGHT', () => this.move(1));
    kb.on('keydown-UP', () => this.move(-this.cols));
    kb.on('keydown-DOWN', () => this.move(this.cols));
    kb.on('keydown-ENTER', () => this.start(this.selected));
    kb.on('keydown-SPACE', () => this.start(this.selected));

    this.layout();
    this.game.events.on('layout', this.layout, this);
    this.scale.on('resize', this.layout, this);
    this.events.once('shutdown', () => {
      this.game.events.off('layout', this.layout, this);
      this.scale.off('resize', this.layout, this);
    });
  }

  bestText(id) {
    try {
      const b = Number(localStorage.getItem(`raul-best-${id}`)) || 0;
      return b ? `recorde: ${b} moedas` : 'nova!';
    } catch {
      return '';
    }
  }

  layout() {
    computeLayout(this.game);
    const { width: w, height: h, portrait, controlsHeight: ch, safeTop, dpr } = layout;
    const areaH = h - ch;
    this.cameras.main.setViewport(0, 0, w, areaH).setSize(w, areaH);
    this.cols = portrait ? 2 : 4;
    const rows = Math.ceil(LEVELS.length / this.cols);
    const s = Math.max(2, Math.floor(Math.min(w, areaH) / 200));

    // fundo: ceu com faixa de grama embaixo
    this.bg.clear().fillStyle(0x5aa8e8, 1).fillRect(0, 0, w, areaH);
    this.bg.fillStyle(0x4caf50, 1).fillRect(0, areaH - 10 * s, w, 10 * s);
    this.bg.fillStyle(0x8a5a32, 1).fillRect(0, areaH - 6 * s, w, 6 * s);

    const top = safeTop + 8 * s;
    this.title.setFontSize(18 * s).setStroke('#1b1b2a', 3 * s).setPosition(w / 2, top + 10 * s);
    this.subtitle.setFontSize(7 * s).setStroke('#1b1b2a', 2 * s).setPosition(w / 2, top + 26 * s);

    // grade de cartoes
    const gridTop = top + 36 * s;
    const gridBottom = areaH - 26 * s;
    const gap = 6 * s;
    const cardW = Math.min((w - gap * (this.cols + 1)) / this.cols, 120 * s);
    const thumbH = cardW * (108 / 192);
    const labelH = 18 * s;
    let cardH = thumbH + labelH;
    const fit = (gridBottom - gridTop - gap * (rows - 1)) / rows;
    const k = Math.min(1, fit / cardH);
    const cw = cardW * k;
    cardH *= k;
    const totalW = cw * this.cols + gap * (this.cols - 1);
    const x0 = (w - totalW) / 2;

    this.cards.forEach((card, i) => {
      const col = i % this.cols;
      const row = Math.floor(i / this.cols);
      const itemsInRow = Math.min(this.cols, LEVELS.length - row * this.cols);
      const rowOffset = ((this.cols - itemsInRow) * (cw + gap)) / 2; // centraliza a ultima linha
      const x = x0 + rowOffset + col * (cw + gap);
      const y = gridTop + row * (cardH + gap);
      const th = cw * (108 / 192);
      card.setPosition(x, y);
      card.w = cw;
      card.h = cardH;
      card.thumb.setDisplaySize(cw - 4 * s, th - 4 * s).setPosition(2 * s, 2 * s);
      card.label.setFontSize(Math.max(8, Math.round(6.5 * s * k))).setStroke('#1b1b2a', s).setPosition(cw / 2, th + 1 * s);
      card.best.setFontSize(Math.max(7, Math.round(4.5 * s * k))).setStroke('#1b1b2a', s).setPosition(cw / 2, th + 9 * s * k)
        .setText(this.bestText(LEVELS[i].id));
      card.zone.setPosition(x, y).setSize(cw, cardH);
      card.zone.input.hitArea.setSize(cw, cardH);
    });

    // Raul e o cachorro correndo no rodape
    this.raul.setScale(s / 2).setPosition(w * 0.6, areaH - 10 * s);
    this.dog.setScale(s / 2).setPosition(w * 0.6 - 34 * s, areaH - 10 * s);
    this.s = s;
    this.dpr = dpr;
    this.drawSelection();
  }

  drawSelection() {
    const s = this.s;
    this.cards.forEach((card, i) => {
      const on = i === this.selected;
      card.frame.clear()
        .fillStyle(0x1b1b2a, 0.85).fillRoundedRect(0, 0, card.w, card.h, 3 * s)
        .lineStyle(on ? 2 * s : s, on ? 0xffd23f : 0xffffff, on ? 1 : 0.5).strokeRoundedRect(0, 0, card.w, card.h, 3 * s);
      card.setScale(on ? 1.03 : 1);
    });
  }

  select(i) {
    this.selected = Phaser.Math.Clamp(i, 0, LEVELS.length - 1);
    this.drawSelection();
  }

  move(d) {
    this.select(this.selected + d);
  }

  start(i) {
    if (this.starting) return;
    this.starting = true;
    this.registry.set('level', LEVELS[i].id);
    this.cameras.main.fadeOut(220, 27, 27, 42);
    this.cameras.main.once('camerafadeoutcomplete', () => this.scene.start('Game', { level: LEVELS[i].id }));
  }

  update() {
    // direcional e A da tela tambem navegam no menu
    const t = { left: touch.left, right: touch.right, jump: touch.jump };
    if (t.left && !this.prev.left) this.move(-1);
    if (t.right && !this.prev.right) this.move(1);
    if (t.jump && !this.prev.jump) this.start(this.selected);
    this.prev = t;
    // o Raul corre pelo rodape
    const w = layout.width;
    this.raul.x += 1.2 * this.s;
    this.dog.x = this.raul.x - 34 * this.s;
    if (this.dog.x > w + 40 * this.s) this.raul.x = -10 * this.s;
  }
}
