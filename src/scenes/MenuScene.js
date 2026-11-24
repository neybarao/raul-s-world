import Phaser from 'phaser';
import { LEVELS } from '../levels/index.js';
import { touch, layout, computeLayout } from '../controls.js';
import { playMusic } from '../music.js';

const FONT = { fontFamily: '"Courier New", monospace', fontStyle: 'bold', color: '#ffffff' };

// Seletor de fases: toque num cartao, ou use o direcional / setas e A / Enter.
export default class MenuScene extends Phaser.Scene {
  constructor() {
    super('Menu');
  }

  create() {
    this.registry.set('mode', 'menu');
    playMusic(this, 'musica-menu');
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
    // logo gerada no Magnific e convertida em pixel art (tools/make_logo.py)
    this.logo = this.add.image(0, 0, 'logo').setOrigin(0.5, 0);
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
      card.zone.on('pointerup', (pointer) => {
        if (this.isSwipe(pointer)) return; // arrastar o carrossel nao conta como toque
        if (this.selected === i) this.start(i);
        else this.select(i);
      });
      this.cards.push(card);
    });
    this.dots = this.add.graphics();
    this.carouselReady = false;
    // carrossel: arrastar o dedo para os lados troca de fase
    this.input.on('pointerup', (pointer) => {
      if (!this.carousel || !this.isSwipe(pointer)) return;
      this.move(pointer.upX < pointer.downX ? 1 : -1);
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

  isSwipe(pointer) {
    return Math.abs(pointer.upX - pointer.downX) > 24 * layout.dpr;
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
    this.carouselReady = false; // ao redimensionar, reposiciona sem animacao
    const { width: w, height: h, portrait, controlsHeight: ch, safeTop, dpr } = layout;
    const areaH = h - ch;
    this.cameras.main.setViewport(0, 0, w, areaH).setSize(w, areaH);
    // em pe: carrossel (um cartao grande por vez, desliza para os lados); deitado: grade de 4
    this.carousel = portrait;
    this.cols = portrait ? 1 : 4;
    const rows = Math.ceil(LEVELS.length / this.cols);
    const s = Math.max(2, Math.floor(Math.min(w, areaH) / 200));

    // fundo: ceu com faixa de grama embaixo
    this.bg.clear().fillStyle(0x5aa8e8, 1).fillRect(0, 0, w, areaH);
    this.bg.fillStyle(0x4caf50, 1).fillRect(0, areaH - 10 * s, w, 10 * s);
    this.bg.fillStyle(0x8a5a32, 1).fillRect(0, areaH - 6 * s, w, 6 * s);

    const top = safeTop + 6 * s;
    // logo em escala inteira (pixels nitidos), no maximo 70% da largura e 30% da altura (20% em pe)
    const src = this.textures.get('logo').getSourceImage();
    const lk = Math.max(1, Math.floor(Math.min((w * 0.7) / src.width, (areaH * (portrait ? 0.24 : 0.3)) / src.height)));
    this.tweens.killTweensOf(this.logo);
    this.logo.setScale(lk).setPosition(w / 2, top);
    // flutua de leve, 2 pixels da arte
    this.tweens.add({ targets: this.logo, y: top + 2 * lk, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.inOut' });
    const logoBottom = top + src.height * lk;
    this.subtitle.setFontSize(7 * s).setStroke('#1b1b2a', 2 * s).setPosition(w / 2, logoBottom + 8 * s);

    const gridTop = logoBottom + 16 * s;
    const gridBottom = areaH - (portrait ? 18 : 26) * s;
    const gap = (portrait ? 4 : 6) * s;
    // texto nunca menor que isso na tela (em pixels CSS), para dar para ler no celular
    const minLabel = 12 * dpr;
    const minBest = 9 * dpr;
    this.dots.clear();
    if (portrait) this.layoutCarousel(w, s, gridTop, gridBottom, minLabel, minBest);
    else this.layoutGrid(w, s, rows, gridTop, gridBottom, gap, minLabel, minBest);

    // Raul e o cachorro correndo no rodape
    this.raul.setScale(s / 2).setPosition(w * 0.6, areaH - 10 * s);
    this.dog.setScale(s / 2).setPosition(w * 0.6 - 34 * s, areaH - 10 * s);
    this.s = s;
    this.dpr = dpr;
    this.drawSelection();
  }

  layoutGrid(w, s, rows, gridTop, gridBottom, gap, minLabel, minBest) {
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
      card.cardW = cw;
      card.cardH = cardH;
      card.thumb.setDisplaySize(cw - 4 * s, th - 4 * s).setPosition(2 * s, 2 * s);
      card.label.setOrigin(0.5, 0).setFontSize(Math.max(minLabel, Math.round(6.5 * s * k))).setStroke('#1b1b2a', s)
        .setPosition(cw / 2, th + 1 * s);
      card.best.setOrigin(0.5, 0).setFontSize(Math.max(minBest, Math.round(4.5 * s * k))).setStroke('#1b1b2a', s)
        .setPosition(cw / 2, th + 9 * s * k).setText(this.bestText(LEVELS[i].id));
      card.zone.setPosition(x, y).setSize(cw, cardH);
      card.zone.input.hitArea.setSize(cw, cardH);
    });
  }

  layoutCarousel(w, s, top, bottom, minLabel, minBest) {
    const dpr = layout.dpr;
    const dotsH = 14 * dpr;
    let cw = Math.min(w * 0.84, 560 * dpr);
    const name = Math.max(minLabel * 1.6, Math.round(cw * 0.075));
    const best = Math.max(minBest * 1.4, Math.round(name * 0.58));
    const pad = Math.round(cw * 0.03);
    const labelH = pad * 2 + name + best * 1.6;
    // a altura do cartao tem que caber entre o subtitulo e os pontinhos
    const maxH = bottom - top - dotsH;
    const thumbFor = (c) => (c - 2 * pad) * (108 / 192);
    if (thumbFor(cw) + pad + labelH > maxH) cw = (maxH - pad - labelH) * (192 / 108) + 2 * pad;
    const th = thumbFor(cw);
    const ch = pad + th + labelH;
    this.carouselGeo = { w, cw, ch, gap: Math.round(cw * 0.06), y: top + Math.max(0, (maxH - ch) / 2) };

    this.cards.forEach((card, i) => {
      card.cardW = cw;
      card.cardH = ch;
      card.thumb.setDisplaySize(cw - 2 * pad, th).setPosition(pad, pad);
      card.label.setOrigin(0.5, 0).setFontSize(name).setStroke('#1b1b2a', s).setPosition(cw / 2, pad + th + pad);
      card.best.setOrigin(0.5, 0).setFontSize(best).setStroke('#1b1b2a', s)
        .setPosition(cw / 2, pad + th + pad + name * 1.25).setText(this.bestText(LEVELS[i].id));
    });

    // pontinhos embaixo: quantas fases e qual esta escolhida
    const dy = this.carouselGeo.y + ch + dotsH * 0.8;
    this.dotsGeo = { y: dy, r: 3 * dpr, gap: 12 * dpr };
  }

  // posiciona os cartoes do carrossel em volta do escolhido (com animacao ao trocar)
  positionCarousel(animate) {
    const g = this.carouselGeo;
    if (!g) return;
    this.cards.forEach((card, i) => {
      const d = i - this.selected;
      const sc = d === 0 ? 1 : 0.86;
      const x = g.w / 2 - g.cw / 2 + d * (g.cw + g.gap) + (g.cw * (1 - sc)) / 2;
      const y = g.y + (g.ch * (1 - sc)) / 2;
      const props = { x, y, scaleX: sc, scaleY: sc, alpha: d === 0 ? 1 : Math.abs(d) === 1 ? 0.6 : 0 };
      this.tweens.killTweensOf(card);
      if (animate) this.tweens.add({ targets: card, ...props, duration: 220, ease: 'Cubic.out' });
      else card.setPosition(x, y).setScale(sc).setAlpha(props.alpha);
      // area de toque fica onde o cartao vai parar
      card.zone.setPosition(x, y).setSize(g.cw * sc, g.ch * sc);
      card.zone.input.hitArea.setSize(g.cw * sc, g.ch * sc);
    });
    const { y, r, gap } = this.dotsGeo;
    const x0 = g.w / 2 - ((LEVELS.length - 1) * gap) / 2;
    this.dots.clear();
    LEVELS.forEach((_, i) => {
      const on = i === this.selected;
      this.dots.fillStyle(0x1b1b2a, 0.6).fillCircle(x0 + i * gap, y + r * 0.4, (on ? r * 1.6 : r) + r * 0.4);
      this.dots.fillStyle(on ? 0xffd23f : 0xffffff, on ? 1 : 0.8).fillCircle(x0 + i * gap, y, on ? r * 1.6 : r);
    });
  }

  drawSelection() {
    const s = this.s;
    this.cards.forEach((card, i) => {
      const on = i === this.selected;
      card.frame.clear()
        .fillStyle(0x1b1b2a, 0.85).fillRoundedRect(0, 0, card.cardW, card.cardH, 3 * s)
        .lineStyle(on ? 2 * s : s, on ? 0xffd23f : 0xffffff, on ? 1 : 0.5).strokeRoundedRect(0, 0, card.cardW, card.cardH, 3 * s);
      if (!this.carousel) card.setScale(on ? 1.03 : 1).setAlpha(1);
    });
    if (this.carousel) this.positionCarousel(this.carouselReady);
    this.carouselReady = true;
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
