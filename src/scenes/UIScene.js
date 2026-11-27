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
    // controles de toque em pixel art (controls.png, gerado por tools/make_controls.py)
    const ctl = (frame) => this.add.image(0, 0, 'controls', frame).setOrigin(0, 0).setVisible(false);
    this.ctl = {
      grille: ctl('grille'),
      dpad: ctl('dpad'),
      run: ctl('btn-ring'),
      jump: ctl('btn-ring'),
      lblRun: ctl('lbl-b'),
      lblJump: ctl('lbl-a'),
      start: ctl('start'),
    };
    this.startDown = false;
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
    this.startZone = this.add.zone(0, 0, 10, 10).setOrigin(0, 0).setInteractive();
    this.startZone.on('pointerdown', () => { this.startDown = true; this.refreshControls(); this.togglePause(); });
    const startUp = () => { if (this.startDown) { this.startDown = false; this.refreshControls(); } };
    this.startZone.on('pointerup', startUp);
    this.startZone.on('pointerout', startUp);

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

  // Controles no estilo dos portateis antigos: direcional em cruz, A (pular), B (arremessar/correr), START (pausa).
  // Sao sprites em pixel art ampliados por um numero inteiro (k), entao cada pixel fica nitido.
  // Medidas em pixels do sprite: cruz de 41 px (centro em 20.5), botao de 23 px (aro de 31) com centro em 16.
  defineButtons() {
    const { width: w, height: h, portrait, hasTouch, controlsHeight: ch } = layout;
    this.pad = null;
    this.btns = [];
    this.start = null;
    this.grillePos = null;
    if (!hasTouch) return;
    if (portrait) {
      const top = h - ch;
      const usable = ch - layout.safeBottom;
      const k = Math.max(1, Math.floor(Math.min((usable * 0.6) / 41, (w * 0.34) / 41, (w * 0.235) / 31)));
      const cy = top + Math.max(23 * k, usable * 0.42);
      this.k = k;
      this.pad = { x: w * 0.23, y: cy, size: 20.5 * k };
      this.btns.push({ id: 'run', x: w * 0.635, y: cy + 7 * k, r: 11.5 * k });
      this.btns.push({ id: 'jump', x: w * 0.845, y: cy - 7 * k, r: 11.5 * k });
      const low = Math.min(cy + 27 * k, top + usable - 7 * k);
      this.start = { x: w * 0.43, y: low, w: 26 * k, h: 9 * k };
      this.grillePos = { x: w * 0.845 + 11 * k, y: low + 6 * k };
    } else {
      const k = Math.max(1, Math.floor(Math.min(h * 0.26, 160 * layout.dpr) / 41));
      this.k = k;
      const cy = h - 30 * k - layout.safeBottom;
      this.pad = { x: 31 * k + layout.safeBottom, y: cy, size: 20.5 * k };
      this.btns.push({ id: 'run', x: w - 54 * k, y: cy + 7 * k, r: 11.5 * k });
      this.btns.push({ id: 'jump', x: w - 22 * k, y: cy - 7 * k, r: 11.5 * k });
    }
  }

  // coloca um sprite com escala k de modo que o ponto (ox, oy) do sprite caia em (cx, cy)
  placeCtl(img, cx, cy, ox, oy) {
    const k = this.k;
    img.setScale(k).setPosition(Math.round(cx - ox * k), Math.round(cy - oy * k)).setVisible(true);
  }

  drawControls() {
    const { width: w, height: h, portrait, controlsHeight: ch } = layout;
    const c = this.ctl;
    this.panel.clear();
    Object.values(c).forEach((o) => o.setVisible(false).clearTint().setAlpha(1));
    this.startZone.setVisible(false);
    if (this.startZone.input) this.startZone.input.enabled = false;
    if (!this.pad) return;
    const k = this.k;

    if (portrait) {
      // corpo do console: faixa azul-marinho da moldura da tela, filete claro e plastico bege
      const top = h - ch;
      this.panel.fillStyle(0xcdbdb0, 1).fillRect(0, top, w, ch);
      this.panel.fillStyle(0x222f52, 1).fillRect(0, top, w, 2 * k);
      this.panel.fillStyle(0xddd0c4, 1).fillRect(0, top + 2 * k, w, k);
      this.placeCtl(c.grille, this.grillePos.x, this.grillePos.y, 22, 14);
    }

    this.placeCtl(c.dpad, this.pad.x, this.pad.y, 20.5, 20.5);
    for (const b of this.btns) {
      const img = c[b.id];
      const lbl = b.id === 'run' ? c.lblRun : c.lblJump;
      this.placeCtl(img, b.x, b.y, 16, 16);
      if (portrait) {
        // letra embaixo do botao, como no console
        this.placeCtl(lbl, b.x, b.y + 20 * k, 3.5, 3.5);
      } else {
        // deitado: por cima do cenario, meio transparente, letra branca no meio do botao
        img.setAlpha(0.6);
        this.placeCtl(lbl, b.x, b.y, 3.5, 3.5);
        lbl.setTintFill(0xffffff).setAlpha(0.75);
      }
    }
    if (!portrait) c.dpad.setAlpha(0.6);

    if (this.start) {
      const st = this.start;
      this.placeCtl(c.start, st.x, st.y, 16, 6.5);
      const zw = st.w + 24 * layout.dpr;
      const zh = st.h + 24 * layout.dpr;
      this.startZone.setVisible(true).setPosition(st.x - zw / 2, st.y - zh / 2).setSize(zw, zh);
      this.startZone.input.hitArea.setSize(zw, zh);
      this.startZone.input.enabled = true;
    }
    this.refreshControls();
  }

  // troca so os quadros (solto/apertado), sem recalcular nada
  refreshControls() {
    if (!this.pad) return;
    const c = this.ctl;
    const ring = layout.portrait ? 'btn-ring' : 'btn';
    c.dpad.setFrame(touch.left ? 'dpad-left' : touch.right ? 'dpad-right' : 'dpad');
    c.run.setFrame(touch.run ? `${ring}-down` : ring);
    c.jump.setFrame(touch.jump ? `${ring}-down` : ring);
    c.start.setFrame(this.startDown ? 'start-down' : 'start');
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
    if (['left', 'right', 'jump', 'run'].some((k) => prev[k] !== touch[k])) this.refreshControls();
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
