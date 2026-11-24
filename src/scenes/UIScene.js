import Phaser from 'phaser';
import { touch, layout, computeLayout } from '../controls.js';

const FONT = { fontFamily: '"Courier New", monospace', fontStyle: 'bold', color: '#ffffff', stroke: '#1b1b2a' };

export default class UIScene extends Phaser.Scene {
  constructor() {
    super('UI');
  }

  create() {
    this.hud = { hearts: 3, max: 3, coins: 0 };
    this.overlay = null;
    this.paused = false;

    this.panel = this.add.graphics();
    this.buttons = this.add.graphics();
    this.face = this.add.image(0, 0, 'raul-face').setOrigin(0, 0);
    this.faceFrame = this.add.graphics();
    this.heartImgs = [];
    this.coinIcon = this.add.image(0, 0, 'coin').setOrigin(0, 0.5);
    this.coinText = this.add.text(0, 0, 'x 0', FONT).setOrigin(0, 0.5);
    this.pauseBtn = this.add.graphics();
    this.pauseZone = this.add.zone(0, 0, 10, 10).setOrigin(0, 0).setInteractive();
    this.pauseZone.on('pointerdown', () => this.togglePause());

    const ev = this.game.events;
    const onHud = (h) => { this.hud = h; this.drawHud(); };
    const onLayout = () => this.relayout();
    const onWin = (d) => this.showOverlay('Fase completa!', `Moedas: ${d.coins} de ${d.total}`, 'Toque para jogar de novo');
    const onOver = () => this.time.delayedCall(700, () => this.showOverlay('Ops!', 'O Raul ficou sem corações', 'Toque para tentar de novo'));
    ev.on('hud', onHud);
    ev.on('layout', onLayout);
    ev.on('level-complete', onWin);
    ev.on('game-over', onOver);
    this.events.once('shutdown', () => {
      ev.off('hud', onHud); ev.off('layout', onLayout); ev.off('level-complete', onWin); ev.off('game-over', onOver);
    });

    const kb = this.input.keyboard;
    kb.on('keydown-P', () => this.togglePause());
    kb.on('keydown-ESC', () => this.togglePause());
    kb.on('keydown-SPACE', () => this.overlayAction());
    kb.on('keydown-ENTER', () => this.overlayAction());

    this.relayout();
  }

  // escala inteira para os elementos em pixel art continuarem nitidos
  get s() {
    return Phaser.Math.Clamp(Math.floor(Math.min(layout.width, layout.height) / 200), 2, 4);
  }

  relayout() {
    computeLayout(this.game);
    this.cameras.main.setSize(layout.width, layout.height);
    this.defineButtons();
    this.drawHud();
    this.drawControls();
    if (this.overlay) this.positionOverlay();
  }

  // ---------- HUD ----------

  drawHud() {
    if (!this.face) return;
    const s = this.s;
    const m = 6 * s;
    this.face.setScale(s).setPosition(m, m);
    this.faceFrame.clear().lineStyle(s, 0xffffff, 1).strokeRect(m - s, m - s, 21 * s + 2 * s, 24 * s + 2 * s);

    while (this.heartImgs.length < this.hud.max) this.heartImgs.push(this.add.image(0, 0, 'hearts', 0).setOrigin(0, 0));
    this.heartImgs.forEach((h, i) => {
      h.setScale(s).setPosition(m + 25 * s + i * 10 * s, m + 2 * s).setFrame(i < this.hud.hearts ? 0 : 1);
    });

    const right = layout.width - m;
    const pb = 14 * s;
    this.pauseBtn.clear()
      .fillStyle(0x1b1b2a, 0.75).fillRoundedRect(right - pb, m, pb, pb, 3 * s)
      .fillStyle(0xffffff, 1).fillRect(right - pb + 4 * s, m + 3 * s, 2 * s, 8 * s).fillRect(right - pb + 8 * s, m + 3 * s, 2 * s, 8 * s);
    this.pauseZone.setPosition(right - pb - 8, m - 8).setSize(pb + 16, pb + 16);
    if (this.pauseZone.input) this.pauseZone.input.hitArea.setSize(pb + 16, pb + 16);

    this.coinIcon.setScale(s * 0.8).setPosition(right - pb - 60 * s, m + pb / 2);
    this.coinText.setFontSize(9 * s).setStroke('#1b1b2a', s * 1.5).setPosition(right - pb - 50 * s, m + pb / 2).setText(`x ${this.hud.coins}`);
  }

  // ---------- controles de toque ----------

  defineButtons() {
    const { width: w, height: h, portrait, hasTouch, controlsHeight: ch } = layout;
    this.btns = [];
    if (!hasTouch) return;
    if (portrait) {
      const cy = h - ch / 2;
      const r = Math.min(ch * 0.3, w * 0.12);
      this.btns.push({ id: 'left', x: w * 0.16, y: cy, r });
      this.btns.push({ id: 'right', x: w * 0.44, y: cy, r });
      this.btns.push({ id: 'jump', x: w * 0.80, y: cy, r: r * 1.25 });
    } else {
      const r = Math.min(h * 0.11, 70);
      const cy = h - r * 1.5;
      this.btns.push({ id: 'left', x: r * 1.6, y: cy, r });
      this.btns.push({ id: 'right', x: r * 4.1, y: cy, r });
      this.btns.push({ id: 'jump', x: w - r * 1.9, y: cy, r: r * 1.25 });
    }
  }

  drawControls() {
    const g = this.buttons;
    const { width: w, height: h, portrait, controlsHeight: ch } = layout;
    this.panel.clear();
    g.clear();
    if (!this.btns.length) return;
    if (portrait) {
      this.panel.fillStyle(0x23233a, 1).fillRect(0, h - ch, w, ch);
      this.panel.fillStyle(0x3a3a5c, 1).fillRect(0, h - ch, w, 3);
    }
    const alpha = portrait ? 1 : 0.45;
    for (const b of this.btns) {
      const on = touch[b.id];
      g.fillStyle(on ? 0xffd23f : b.id === 'jump' ? 0xe8463a : 0x4a4a74, alpha).fillCircle(b.x, b.y, b.r);
      g.lineStyle(3, 0x11111c, alpha).strokeCircle(b.x, b.y, b.r);
      g.fillStyle(0xffffff, portrait ? 1 : 0.8);
      const a = b.r * 0.38;
      if (b.id === 'left') g.fillTriangle(b.x - a, b.y, b.x + a * 0.7, b.y - a, b.x + a * 0.7, b.y + a);
      if (b.id === 'right') g.fillTriangle(b.x + a, b.y, b.x - a * 0.7, b.y - a, b.x - a * 0.7, b.y + a);
      if (b.id === 'jump') g.fillTriangle(b.x, b.y - a, b.x - a, b.y + a * 0.6, b.x + a, b.y + a * 0.6);
    }
  }

  update() {
    if (!this.btns || !this.btns.length) return;
    const prev = { ...touch };
    touch.left = touch.right = touch.jump = false;
    // le todos os dedos na tela, assim da pra correr e pular ao mesmo tempo
    for (const p of this.input.manager.pointers) {
      if (!p.isDown || p.wasTouch === false) continue;
      // cada dedo aciona so o botao mais proximo, com area de toque maior que o desenho
      let best = null;
      let bestD = Infinity;
      for (const b of this.btns) {
        const d = Phaser.Math.Distance.Between(p.x, p.y, b.x, b.y);
        if (d <= b.r * 1.5 && d < bestD) { best = b; bestD = d; }
      }
      if (best) touch[best.id] = true;
    }
    if (prev.left !== touch.left || prev.right !== touch.right || prev.jump !== touch.jump) this.drawControls();
  }

  // ---------- pausa e telas de mensagem ----------

  togglePause() {
    if (this.overlay && !this.paused) return;
    const game = this.scene.get('Game');
    if (!this.paused) {
      this.paused = true;
      game.scene.pause();
      this.showOverlay('Pausado', '', 'Toque para continuar');
    } else {
      this.paused = false;
      this.hideOverlay();
      game.scene.resume();
    }
  }

  showOverlay(title, subtitle, hint) {
    this.hideOverlay();
    const o = this.add.container(0, 0).setDepth(100);
    o.bg = this.add.rectangle(0, 0, 10, 10, 0x11111c, 0.72).setOrigin(0, 0).setInteractive();
    o.title = this.add.text(0, 0, title, FONT).setOrigin(0.5);
    o.sub = this.add.text(0, 0, subtitle, FONT).setOrigin(0.5);
    o.hint = this.add.text(0, 0, hint, { ...FONT, color: '#ffd23f' }).setOrigin(0.5);
    o.add([o.bg, o.title, o.sub, o.hint]);
    this.tweens.add({ targets: o.hint, alpha: 0.35, duration: 600, yoyo: true, repeat: -1 });
    o.bg.on('pointerdown', () => this.overlayAction());
    this.overlay = o;
    this.positionOverlay();
  }

  positionOverlay() {
    const o = this.overlay;
    const s = this.s;
    const { width: w, height: h } = layout;
    o.bg.setSize(w, h);
    o.bg.input.hitArea.setSize(w, h);
    o.title.setFontSize(16 * s).setStroke('#1b1b2a', 2 * s).setPosition(w / 2, h * 0.38);
    o.sub.setFontSize(8 * s).setStroke('#1b1b2a', s).setPosition(w / 2, h * 0.38 + 18 * s);
    o.hint.setFontSize(7 * s).setStroke('#1b1b2a', s).setPosition(w / 2, h * 0.38 + 34 * s);
  }

  hideOverlay() {
    if (this.overlay) this.overlay.destroy();
    this.overlay = null;
  }

  overlayAction() {
    if (!this.overlay) return;
    if (this.paused) return this.togglePause();
    this.hideOverlay();
    this.scene.get('Game').scene.restart();
  }
}
