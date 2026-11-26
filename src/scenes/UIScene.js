import Phaser from 'phaser';
import { touch, layout, computeLayout } from '../controls.js';
import { isMuted, toggleMute, setMusicPaused } from '../music.js';

// Expressoes do retrato (quadros de raul-faces.png, gerado por tools/make_faces.py)
const FACE = { feliz: 0, rindo: 1, surpreso: 2, piscando: 3, triste: 4 };
// reacao a cada evento do jogo: expressao, duracao (ms, 0 = fica) e prioridade
const REACTIONS = {
  coin: { face: 'rindo', ms: 450, pri: 1 },
  mola: { face: 'surpreso', ms: 650, pri: 1 },
  throw: { face: 'piscando', ms: 400, pri: 1 },
  enemy: { face: 'piscando', ms: 800, pri: 2 },
  hurt: { face: 'triste', ms: 1400, pri: 3 },
  win: { face: 'rindo', ms: 0, pri: 4 },
  over: { face: 'triste', ms: 0, pri: 4 },
};

// quadros de hud-counter.png (gerado por tools/make_hud_icons.py): 0-9, "x" e a moedinha
const COUNTER = { x: 10, coin: 11 };

const FONT = { fontFamily: '"Courier New", monospace', fontStyle: 'bold', color: '#ffffff', stroke: '#1b1b2a' };

export default class UIScene extends Phaser.Scene {
  constructor() {
    super('UI');
  }

  create() {
    this.hud = { hearts: 3, max: 3, coins: 0 };
    this.mode = this.registry.get('mode') || 'menu';
    this.overlay = null;
    this.paused = false;

    this.panel = this.add.graphics();
    this.buttons = this.add.graphics();
    this.face = this.add.image(0, 0, 'raul-faces', FACE.feliz).setOrigin(0, 0);
    this.faceState = { face: 'feliz', pri: 0, until: 0, timer: null };
    this.faceHop = { x: 0, y: 0 };
    this.heartImgs = [];
    // contador de moedas: moedinha + "x" + numeros, tudo em pixel art (hud-counter.png)
    this.coinPill = this.add.graphics();
    this.coinIcon = this.add.image(0, 0, 'hud-counter', COUNTER.coin).setOrigin(0, 0);
    this.coinDigits = [];
    // botoes com icones da biblioteca Pixelarticons (hud-buttons.png)
    this.pauseBtn = this.add.image(0, 0, 'hud-buttons', 0).setOrigin(0, 0);
    this.pauseZone = this.add.zone(0, 0, 10, 10).setOrigin(0, 0).setInteractive();
    this.pauseZone.on('pointerdown', () => this.togglePause());
    // botao de som (liga/desliga a musica), aparece no menu e no jogo
    this.soundBtn = this.add.image(0, 0, 'hud-buttons', 1).setOrigin(0, 0);
    this.soundZone = this.add.zone(0, 0, 10, 10).setOrigin(0, 0).setInteractive();
    this.soundZone.on('pointerdown', () => { toggleMute(); this.drawHud(); });
    this.labels = [0, 1, 2].map(() => this.add.text(0, 0, '', FONT).setOrigin(0.5).setVisible(false));
    this.startZone = this.add.zone(0, 0, 10, 10).setOrigin(0, 0).setInteractive();
    this.startZone.on('pointerdown', () => this.togglePause());

    const ev = this.game.events;
    const onHud = (h) => { this.hud = h; this.drawHud(); };
    const onLayout = () => this.relayout();
    const onWin = (d) => this.showOverlay('Fase completa!', `Moedas: ${d.coins} de ${d.total}`, 'Toque para escolher outra fase', { kind: 'win', light: true });
    const onOver = () => this.time.delayedCall(1800, () => this.mode === 'game' && this.showOverlay('Ai, ai, ai!', 'O Raul se machucou', 'Toque para tentar de novo', { light: true, menu: true }));
    const onMode = (m) => { this.mode = m; this.paused = false; this.hideOverlay(); this.resetFace(); this.drawHud(); };
    const onFace = (kind) => this.react(kind);
    ev.on('face', onFace);
    ev.on('hud', onHud);
    ev.on('layout', onLayout);
    ev.on('level-complete', onWin);
    ev.on('game-over', onOver);
    ev.on('mode', onMode);
    this.events.once('shutdown', () => {
      ev.off('hud', onHud); ev.off('layout', onLayout); ev.off('level-complete', onWin); ev.off('game-over', onOver); ev.off('mode', onMode); ev.off('face', onFace);
    });

    const kb = this.input.keyboard;
    kb.on('keydown-P', () => this.togglePause());
    kb.on('keydown-M', () => { toggleMute(); this.drawHud(); });
    kb.on('keydown-ESC', () => this.togglePause());
    kb.on('keydown-SPACE', () => this.overlayAction());
    kb.on('keydown-ENTER', () => this.overlayAction());

    this.relayout();
  }

  // escala inteira para os elementos em pixel art continuarem nitidos
  get s() {
    return Phaser.Math.Clamp(Math.floor(Math.min(layout.width, layout.height) / 200), 2, 12);
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
    // no seletor de fases o HUD some
    const show = this.mode !== 'menu';
    [this.face, this.coinPill, this.coinIcon, this.pauseBtn, ...this.heartImgs, ...this.coinDigits].forEach((o) => o.setVisible(show));
    if (this.pauseZone.input) this.pauseZone.input.enabled = show;
    const s = this.s;
    const m = 6 * s;
    // no iPhone o sistema embaca uma faixa abaixo do relogio: o HUD desce um pouco mais
    const top0 = layout.safeTop + (layout.safeTop > 0 ? 12 * layout.dpr : 0);
    const top = m + top0;
    const right = layout.width - m;

    // botoes de som e pausa no canto direito (som a esquerda da pausa; no menu so o som)
    const bs = this.buttonScale;
    const bw = 30 * bs;
    const gap = 3 * bs;
    const pauseX = right - bw;
    const soundX = show ? pauseX - gap - bw : right - bw;
    this.soundBtn.setScale(bs).setPosition(soundX, top).setFrame(isMuted() ? 2 : 1);
    this.pauseBtn.setScale(bs).setPosition(pauseX, top);
    this.placeZone(this.soundZone, soundX, top, bw);
    this.placeZone(this.pauseZone, pauseX, top, bw);
    if (!show) return;

    // retrato, coracoes e moedas no mesmo tamanho de pixel (escala inteira, fica nitido)
    const k = this.hudScale;
    const fx = m;
    const fy = top;
    this.faceBase = { x: fx, y: fy, k };
    this.face.setScale(k).setPosition(fx + this.faceHop.x, fy + this.faceHop.y);
    const fw = this.face.displayWidth;
    const fh = this.face.displayHeight;
    const col = fx + fw + 4 * k;

    // coracoes na parte de cima, ao lado do retrato
    while (this.heartImgs.length < this.hud.max) this.heartImgs.push(this.add.image(0, 0, 'hearts', 0).setOrigin(0, 0));
    const heartsY = fy + 9 * k;
    this.heartImgs.forEach((h, i) => {
      h.setScale(k).setPosition(col + i * 20 * k, heartsY).setFrame(i < this.hud.hearts ? 0 : 1);
    });

    // moedas logo abaixo dos coracoes, numa plaquinha escura
    const glyphs = ['x', ...String(this.hud.coins)];
    while (this.coinDigits.length < glyphs.length) this.coinDigits.push(this.add.image(0, 0, 'hud-counter', 0).setOrigin(0, 0));
    const pillY = heartsY + 16 * k + 4 * k;
    const pillH = 14 * k;
    const textW = glyphs.length * 7 * k - (glyphs.length - 1) * k; // numeros encostados pelo contorno
    const pillW = 3 * k + 12 * k + 2 * k + textW + 4 * k;
    this.coinPill.clear()
      .fillStyle(0x1b1b2a, 1).fillRect(col + k, pillY, pillW - 2 * k, pillH).fillRect(col, pillY + k, pillW, pillH - 2 * k)
      .fillStyle(0x2b2d48, 0.92).fillRect(col + 2 * k, pillY + k, pillW - 4 * k, pillH - 2 * k).fillRect(col + k, pillY + 2 * k, pillW - 2 * k, pillH - 4 * k);
    this.coinIcon.setScale(k).setPosition(col + 2 * k, pillY + k);
    let tx = col + 3 * k + 12 * k;
    this.coinDigits.forEach((d, i) => {
      if (i >= glyphs.length) { d.setVisible(false); return; }
      const g = glyphs[i];
      d.setVisible(true).setScale(k).setFrame(g === 'x' ? COUNTER.x : Number(g)).setPosition(tx, pillY + 2 * k);
      tx += 6 * k;
    });
  }

  placeZone(zone, x, y, size) {
    const pad = 6 * layout.dpr;
    zone.setPosition(x - pad, y - pad).setSize(size + 2 * pad, size + 2 * pad);
    if (zone.input) zone.input.hitArea.setSize(size + 2 * pad, size + 2 * pad);
  }

  get buttonScale() {
    return Math.max(2, Math.round(this.hudScale * 0.7));
  }

  get hudScale() {
    return Math.max(2, Math.round(this.s * 0.7));
  }

  // ---------- retrato reagindo ao jogo ----------

  react(kind) {
    const r = REACTIONS[kind];
    if (!r || !this.face) return;
    const st = this.faceState;
    const now = this.time.now;
    const busy = st.pri >= 4 || (st.until > now && st.pri > r.pri);
    if (busy) return;
    if (st.timer) st.timer.remove();
    st.timer = null;
    st.face = r.face;
    st.pri = r.pri;
    st.until = r.ms ? now + r.ms : Infinity;
    this.face.setFrame(FACE[r.face]);
    if (r.ms) st.timer = this.time.delayedCall(r.ms, () => this.resetFace());
    this.hopFace(kind === 'hurt' || kind === 'over' ? 'shake' : 'hop');
  }

  resetFace() {
    const st = this.faceState;
    if (!st) return;
    if (st.timer) st.timer.remove();
    st.timer = null;
    st.face = 'feliz';
    st.pri = 0;
    st.until = 0;
    if (this.face) this.face.setFrame(FACE.feliz);
  }

  // pulinho (ou tremida, quando se machuca) em passos de pixel inteiro
  hopFace(type) {
    const k = this.hudScale;
    const steps = type === 'shake' ? [[-k, 0], [k, 0], [-k, 0], [k, 0], [0, 0]] : [[0, -2 * k], [0, -k], [0, 0]];
    this.tweens.killTweensOf(this.faceHop);
    this.faceHop.x = 0;
    this.faceHop.y = 0;
    steps.forEach(([x, y], i) => {
      this.time.delayedCall(i * 55, () => {
        this.faceHop.x = x;
        this.faceHop.y = y;
        if (this.faceBase) this.face.setPosition(this.faceBase.x + x, this.faceBase.y + y);
      });
    });
  }

  // ---------- controles de toque ----------

  // Controles no estilo dos portateis antigos: direcional em cruz, A (pular), B (correr), START (pausa).
  defineButtons() {
    const { width: w, height: h, portrait, hasTouch, controlsHeight: ch } = layout;
    this.pad = null;
    this.btns = [];
    this.start = null;
    if (!hasTouch) return;
    if (portrait) {
      const top = h - ch;
      const usable = ch - layout.safeBottom;
      const cy = top + usable * 0.46;
      const size = Math.min(ch * 0.3, w * 0.15); // meio comprimento de cada braco da cruz
      const r = Math.min(ch * 0.15, w * 0.085);
      this.pad = { x: w * 0.25, y: cy, size };
      this.btns.push({ id: 'run', label: 'B', x: w * 0.67, y: cy + r * 0.55, r });
      this.btns.push({ id: 'jump', label: 'A', x: w * 0.86, y: cy - r * 0.55, r });
      this.start = { x: w * 0.5, y: top + usable * 0.86, w: Math.min(w * 0.16, 70 * layout.dpr), h: Math.max(10 * layout.dpr, ch * 0.055) };
    } else {
      const size = Math.min(h * 0.13, 80 * layout.dpr);
      const r = Math.min(h * 0.075, 46 * layout.dpr);
      const cy = h - size * 1.45;
      this.pad = { x: size * 1.5, y: cy, size };
      this.btns.push({ id: 'run', label: 'B', x: w - r * 4.6, y: cy + r * 0.6, r });
      this.btns.push({ id: 'jump', label: 'A', x: w - r * 1.8, y: cy - r * 0.6, r });
    }
  }

  drawControls() {
    const g = this.buttons;
    const { width: w, height: h, portrait, controlsHeight: ch } = layout;
    this.panel.clear();
    g.clear();
    this.labels.forEach((t) => t.setVisible(false));
    this.startZone.setVisible(false);
    if (this.startZone.input) this.startZone.input.enabled = false;
    if (!this.pad) return;
    const solid = portrait;
    const a = solid ? 1 : 0.4;
    const u = layout.dpr;

    if (portrait) {
      // corpo do console
      const top = h - ch;
      this.panel.fillStyle(0x16162a, 1).fillRect(0, top, w, 6 * u);
      this.panel.fillStyle(0xcfcabd, 1).fillRect(0, top + 6 * u, w, ch - 6 * u);
      this.panel.fillStyle(0xe2ddd1, 1).fillRect(0, top + 6 * u, w, 3 * u);
      // grade do alto-falante
      for (let i = 0; i < 5; i++) {
        const x = w - (24 + i * 9) * u;
        this.panel.fillStyle(0xa9a394, 1).fillRoundedRect(x, h - layout.safeBottom - ch * 0.22, 4 * u, ch * 0.16, 2 * u);
      }
    }

    // direcional em cruz
    const { x, y, size } = this.pad;
    const arm = size * 0.66;
    const shadow = Math.max(2, size * 0.06);
    g.fillStyle(0x000000, solid ? 0.25 : 0.15)
      .fillRoundedRect(x - size + shadow, y - arm / 2 + shadow, size * 2, arm, 4 * u)
      .fillRoundedRect(x - arm / 2 + shadow, y - size + shadow, arm, size * 2, 4 * u);
    g.fillStyle(0x2b2b30, a)
      .fillRoundedRect(x - size, y - arm / 2, size * 2, arm, 4 * u)
      .fillRoundedRect(x - arm / 2, y - size, arm, size * 2, 4 * u);
    const lit = 0x55555e;
    if (touch.left) g.fillStyle(lit, a).fillRoundedRect(x - size, y - arm / 2, size - arm / 2, arm, 4 * u);
    if (touch.right) g.fillStyle(lit, a).fillRoundedRect(x + arm / 2, y - arm / 2, size - arm / 2, arm, 4 * u);
    g.fillStyle(0x1e1e22, a).fillCircle(x, y, arm * 0.28);
    const t = arm * 0.22;
    const tri = 0x6b6b74;
    g.fillStyle(tri, a)
      .fillTriangle(x - size + t * 0.9, y, x - size + t * 2.3, y - t, x - size + t * 2.3, y + t)
      .fillTriangle(x + size - t * 0.9, y, x + size - t * 2.3, y - t, x + size - t * 2.3, y + t)
      .fillTriangle(x, y - size + t * 0.9, x - t, y - size + t * 2.3, x + t, y - size + t * 2.3)
      .fillTriangle(x, y + size - t * 0.9, x - t, y + size - t * 2.3, x + t, y + size - t * 2.3);

    // botoes A e B
    let li = 0;
    for (const b of this.btns) {
      const on = touch[b.id];
      if (portrait) g.fillStyle(0xb9b3a5, 1).fillCircle(b.x, b.y, b.r * 1.18);
      g.fillStyle(0x000000, solid ? 0.3 : 0.15).fillCircle(b.x + shadow, b.y + shadow, b.r);
      g.fillStyle(on ? 0xd9407f : 0xa3195b, a).fillCircle(b.x, b.y, b.r);
      g.fillStyle(0xffffff, on ? 0.1 : 0.22 * a).fillCircle(b.x - b.r * 0.3, b.y - b.r * 0.3, b.r * 0.35);
      const lbl = this.labels[li++];
      lbl.setText(b.label).setFontSize(Math.round(b.r * 0.62)).setVisible(true).setAlpha(solid ? 1 : 0.6)
        .setPosition(b.x + (portrait ? b.r * 0.9 : 0), b.y + (portrait ? b.r * 1.15 : 0))
        .setColor(portrait ? '#2b2a6b' : '#ffffff').setStroke(portrait ? '#cfcabd' : '#1b1b2a', portrait ? 0 : 3 * u);
    }

    // START (pausa)
    if (this.start) {
      const st = this.start;
      g.fillStyle(0x8f8a7e, 1).fillRoundedRect(st.x - st.w / 2, st.y - st.h / 2, st.w, st.h, st.h / 2);
      const lbl = this.labels[li++];
      lbl.setText('START').setFontSize(Math.round(Math.max(9 * u, st.h * 0.95))).setVisible(true).setAlpha(1)
        .setPosition(st.x, st.y + st.h * 1.3).setColor('#2b2a6b').setStroke('#cfcabd', 0);
      this.startZone.setVisible(true).setPosition(st.x - st.w / 2 - 10 * u, st.y - st.h / 2 - 12 * u).setSize(st.w + 20 * u, st.h + 30 * u);
      this.startZone.input.hitArea.setSize(st.w + 20 * u, st.h + 30 * u);
      this.startZone.input.enabled = true;
    }
  }

  update() {
    if (!this.pad) return;
    const prev = { ...touch };
    touch.left = touch.right = touch.jump = touch.run = false;
    // le todos os dedos na tela, assim da pra andar, correr e pular ao mesmo tempo
    for (const p of this.input.manager.pointers) {
      if (!p.isDown || p.wasTouch === false) continue;
      const { x, y, size } = this.pad;
      const dx = p.x - x;
      const dy = p.y - y;
      if (Math.hypot(dx, dy) <= size * 1.5) {
        // o direcional so precisa de esquerda e direita; diagonais tambem valem
        if (Math.abs(dx) > size * 0.15) touch[dx < 0 ? 'left' : 'right'] = true;
        continue;
      }
      let best = null;
      let bestD = Infinity;
      for (const b of this.btns) {
        const d = Phaser.Math.Distance.Between(p.x, p.y, b.x, b.y);
        if (d <= b.r * 1.6 && d < bestD) { best = b; bestD = d; }
      }
      if (best) touch[best.id] = true;
    }
    if (['left', 'right', 'jump', 'run'].some((k) => prev[k] !== touch[k])) this.drawControls();
  }

  // ---------- pausa e telas de mensagem ----------

  togglePause() {
    if (this.mode === 'menu') return;
    if (this.overlay && !this.paused) return;
    const game = this.scene.get('Game');
    if (!this.paused) {
      this.paused = true;
      game.scene.pause();
      setMusicPaused(true);
      this.showOverlay('Pausado', '', 'Toque para continuar', { menu: true });
    } else {
      this.paused = false;
      this.hideOverlay();
      game.scene.resume();
      setMusicPaused(false);
    }
  }

  showOverlay(title, subtitle, hint, opts = {}) {
    this.hideOverlay();
    const o = this.add.container(0, 0).setDepth(100);
    o.bg = this.add.rectangle(0, 0, 10, 10, 0x11111c, opts.light ? 0.3 : 0.72).setOrigin(0, 0).setInteractive();
    o.light = !!opts.light;
    o.title = this.add.text(0, 0, title, FONT).setOrigin(0.5);
    o.sub = this.add.text(0, 0, subtitle, FONT).setOrigin(0.5);
    o.hint = this.add.text(0, 0, hint, { ...FONT, color: '#ffd23f' }).setOrigin(0.5);
    o.add([o.bg, o.title, o.sub, o.hint]);
    o.kind = opts.kind || '';
    if (opts.menu) {
      // botao para voltar ao seletor de fases
      o.menuBtn = this.add.text(0, 0, '« Escolher fase', { ...FONT, backgroundColor: '#2b2a6b' }).setOrigin(0.5).setInteractive();
      o.menuBtn.on('pointerdown', () => this.goToMenu());
      o.add(o.menuBtn);
    }
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
    // na tela de choro o texto fica no alto, para ver o Raul sentado
    const ty = o.light ? h * 0.16 : h * 0.38;
    o.title.setFontSize(16 * s).setStroke('#1b1b2a', 2 * s).setPosition(w / 2, ty);
    o.sub.setFontSize(8 * s).setStroke('#1b1b2a', s).setPosition(w / 2, ty + 18 * s);
    o.hint.setFontSize(7 * s).setStroke('#1b1b2a', s).setPosition(w / 2, ty + 34 * s);
    if (o.menuBtn) o.menuBtn.setFontSize(7 * s).setPadding(5 * s, 3 * s).setPosition(w / 2, ty + 54 * s);
  }

  hideOverlay() {
    if (this.overlay) this.overlay.destroy();
    this.overlay = null;
  }

  overlayAction() {
    if (!this.overlay) return;
    if (this.paused) return this.togglePause();
    const kind = this.overlay.kind;
    this.hideOverlay();
    if (kind === 'win') return this.goToMenu();
    const game = this.scene.get('Game');
    game.scene.restart({ level: this.registry.get('level') });
  }

  goToMenu() {
    this.hideOverlay();
    this.paused = false;
    const game = this.scene.get('Game');
    if (game.scene.isPaused()) game.scene.resume();
    setMusicPaused(false);
    game.scene.start('Menu');
  }
}
