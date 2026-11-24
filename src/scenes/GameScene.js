import Phaser from 'phaser';
import { TILE, U, PLAYER, ENEMY, DOG, VIEW } from '../config.js';
import { touch, layout, computeLayout } from '../controls.js';
import { levelById, ENEMIES } from '../levels/index.js';

const MOLA_BOOST = 1.45; // a mola joga o Raul 45% mais forte que um pulo normal
const BOUNCE_V = 260 * U; // altura do quique da bolinha

// indices do tiles.png
const T = { GRASS: 0, DIRT: 1, GRASS_L: 2, GRASS_R: 3, DIRT_L: 4, DIRT_R: 5, PLAT_L: 6, PLAT: 7, PLAT_R: 8 };

export default class GameScene extends Phaser.Scene {
  constructor() {
    super('Game');
  }

  create(data) {
    this.level = levelById(data?.level || this.registry.get('level'));
    this.registry.set('level', this.level.id);
    this.registry.set('mode', 'game');
    this.game.events.emit('mode', 'game');
    this.enemyDef = ENEMIES[this.level.enemy];
    this.rows = this.level.map;
    this.levelW = this.rows[0].length * TILE;
    this.levelH = this.rows.length * TILE;
    this.state = 'playing';
    this.hearts = PLAYER.maxHearts;
    this.coinCount = 0;
    this.facing = 1;
    this.lastGroundedAt = 0;
    this.jumpPressedAt = -9999;
    this.prevJumpHeld = false;
    this.invulnerableUntil = 0;
    this.knockbackUntil = 0;

    this.physics.world.setBounds(0, 0, this.levelW, this.levelH + 200 * U);
    this.physics.world.setBoundsCollision(true, true, false, false);

    this.buildBackground();
    this.buildTilemap();
    this.spawnEntities();
    this.setupCamera();
    this.setupKeyboard();

    this.scale.on('resize', this.layoutCamera, this);
    this.events.once('shutdown', () => this.scale.off('resize', this.layoutCamera, this));
    this.emitHud();
  }

  // ---------- montagem da fase ----------

  cell(x, y) {
    if (y < 0 || y >= this.rows.length || x < 0 || x >= this.rows[0].length) return ' ';
    return this.rows[y][x];
  }

  buildTilemap() {
    const data = this.rows.map((row, y) =>
      [...row].map((ch, x) => {
        if (ch === '#') {
          const top = this.cell(x, y - 1) !== '#';
          const l = this.cell(x - 1, y) !== '#' && x > 0;
          const r = this.cell(x + 1, y) !== '#' && x < row.length - 1;
          if (top) return l ? T.GRASS_L : r ? T.GRASS_R : T.GRASS;
          return l ? T.DIRT_L : r ? T.DIRT_R : T.DIRT;
        }
        if (ch === '=') {
          const l = this.cell(x - 1, y) !== '=';
          const r = this.cell(x + 1, y) !== '=';
          return l ? T.PLAT_L : r ? T.PLAT_R : T.PLAT;
        }
        return -1;
      })
    );
    const map = this.make.tilemap({ data, tileWidth: TILE, tileHeight: TILE });
    const tileset = map.addTilesetImage(this.level.tiles, this.level.tiles, TILE, TILE, 1, 2);
    this.layer = map.createLayer(0, tileset, 0, 0);
    this.layer.setCollision([T.GRASS, T.DIRT, T.GRASS_L, T.GRASS_R, T.DIRT_L, T.DIRT_R]);
    // plataformas: so colidem por cima, da pra atravessar pulando por baixo
    this.layer.forEachTile((t) => {
      if (t.index >= T.PLAT_L && t.index <= T.PLAT_R) t.setCollision(false, false, true, false);
    });
  }

  buildBackground() {
    const lv = this.level;
    this.cameras.main.setBackgroundColor(lv.sky);
    const groundY = 21 * TILE + 8 * U;
    if (!lv.bg) {
      // floresta: nuvens, morros e arvores desenhados por codigo
      const rnd = new Phaser.Math.RandomDataGenerator(['nuvens']);
      for (let i = 0; i < 14; i++) {
        this.add
          .image(rnd.between(-200 * U, this.levelW * 0.3 + 400 * U), rnd.between(40 * U, 200 * U), 'cloud')
          .setScrollFactor(0.1, 0.6)
          .setAlpha(0.95);
      }
      this.add.tileSprite(-400 * U, groundY, this.levelW + 800 * U, 192, 'hills-far').setOrigin(0, 1).setScrollFactor(0.2, 1);
      this.add.tileSprite(-400 * U, groundY, this.levelW + 800 * U, 192, 'trees-near').setOrigin(0, 1).setScrollFactor(0.45, 1);
    } else {
      // fases das fotos: panorama do Magnific, em dobro, repetindo sem emenda
      const src = this.textures.get(lv.bg).getSourceImage();
      this.add
        .tileSprite(-400 * U, groundY + 40 * U, this.levelW + 800 * U, src.height * 2, lv.bg)
        .setOrigin(0, 1)
        .setTileScale(2, 2)
        .setScrollFactor(0.3, 1);
    }
    if (lv.water) {
      // agua no fundo dos buracos (cair nela continua custando um coracao)
      const top = this.levelH - TILE * 1.4;
      this.add.rectangle(0, top, this.levelW, this.levelH - top + 200, lv.water, 0.92).setOrigin(0, 0).setDepth(-1);
      this.waves = this.add.graphics().setDepth(-1);
      this.waterTop = top;
    }
    if (lv.bubbles) this.makeBubbles();
  }

  makeBubbles() {
    const g = this.make.graphics({ x: 0, y: 0, add: false });
    g.lineStyle(2, 0xdff8ff, 0.9).strokeCircle(6, 6, 4).fillStyle(0xffffff, 0.9).fillRect(4, 3, 2, 2);
    g.generateTexture('bubble', 12, 12);
    g.destroy();
    this.add.particles(0, 0, 'bubble', {
      x: { min: 0, max: this.levelW }, y: this.levelH,
      lifespan: 9000, speedY: { min: -40 * U, max: -20 * U }, speedX: { min: -6, max: 6 },
      scale: { min: 0.6, max: 1.4 }, alpha: { start: 0.9, end: 0 }, frequency: 220, quantity: 1,
    }).setDepth(-1);
  }

  spawnEntities() {
    this.coins = this.physics.add.staticGroup();
    this.molas = this.physics.add.staticGroup();
    this.enemies = this.physics.add.group({ allowGravity: true });
    this.checkpoints = [];

    this.rows.forEach((row, y) =>
      [...row].forEach((ch, x) => {
        const cx = x * TILE + TILE / 2;
        const bottom = (y + 1) * TILE;
        if (ch === 'P') this.spawn = { x: cx, y: bottom };
        if (ch === 'o') {
          const c = this.coins.create(cx, y * TILE + TILE / 2, 'coin');
          c.body.setSize(20, 24);
          this.tweens.add({ targets: c, scaleX: 0.25, duration: 420, yoyo: true, repeat: -1, ease: 'Sine.inOut', delay: x * 40 });
        }
        if (ch === 'e') this.spawnEnemy(cx, bottom, x);
        if (ch === 'T') {
          const m = this.molas.create(cx, bottom, this.level.mola, 0).setOrigin(0.5, 1);
          m.refreshBody();
          m.body.setSize(28, 14).setOffset(2, 10);
        }
        if (ch === 'F') {
          this.flag = this.physics.add.staticImage(cx, bottom, 'flag').setOrigin(0.5, 1);
          this.flag.refreshBody();
          this.flag.body.setSize(20, 112).setOffset(8, 0);
        }
        // pontos de retorno: inicio de cada trecho de chao depois de um buraco
        if (ch === '#' && this.cell(x, y - 1) !== '#' && this.cell(x - 1, y) === ' ' && x > 0) {
          this.checkpoints.push({ x: cx + TILE, y: y * TILE });
        }
      })
    );
    this.respawnPoint = { ...this.spawn };

    this.player = this.physics.add.sprite(this.spawn.x, this.spawn.y, 'raul', 0).setOrigin(0.5, 1);
    this.player.body.setSize(20, 48).setOffset(22, 40);
    this.player.body.setMaxVelocityY(520 * U);
    this.player.setCollideWorldBounds(true);
    this.player.setDepth(10);

    this.dog = this.add.sprite(this.spawn.x - DOG.followGap, this.spawn.y, 'dog', 0).setOrigin(0.5, 1).setDepth(9);
    this.dogTrail = [];
    this.dogIdleMs = 0;
    this.zzz = this.add.text(0, 0, 'z', { fontFamily: 'monospace', fontSize: '16px', color: '#ffffff' }).setDepth(9).setVisible(false);

    this.physics.add.collider(this.player, this.layer);
    this.physics.add.collider(this.enemies, this.layer);
    this.physics.add.overlap(this.player, this.coins, (_p, c) => this.collectCoin(c));
    this.physics.add.overlap(this.player, this.enemies, (_p, e) => this.touchEnemy(e));
    this.physics.add.overlap(this.player, this.flag, () => this.reachFlag());
    this.physics.add.overlap(this.player, this.molas, (_p, m) => this.bounceMola(m));
  }

  spawnEnemy(cx, bottom, x) {
    const def = this.enemyDef;
    const e = this.enemies.create(cx, bottom, def.key).setOrigin(0.5, 1);
    e.body.setSize(def.body[0], def.body[1]).setOffset(def.body[2], def.body[3]);
    e.kind = def.kind;
    e.dir = -1;
    e.play(`${def.key}-walk`);
    if (e.kind === 'floater') {
      // a agua-viva e movida pelo codigo (sobe e desce), sem gravidade
      e.body.allowGravity = false;
      e.body.moves = false;
      e.baseX = cx;
      e.baseY = bottom;
      e.phase = x * 0.7;
    } else {
      e.setVelocityX(-ENEMY.speed);
    }
  }

  setupCamera() {
    const cam = this.cameras.main;
    cam.setBounds(0, 0, this.levelW, this.levelH);
    cam.startFollow(this.player, true, 0.12, 0.1);
    cam.setDeadzone(8 * U, 40 * U);
    this.layoutCamera();
    cam.centerOn(this.player.x, this.player.y);
  }

  layoutCamera() {
    const L = computeLayout(this.game);
    const viewH = L.height - L.controlsHeight;
    const ideal = L.portrait
      ? L.width / (VIEW.portraitTilesWide * TILE)
      : viewH / (VIEW.landscapeTilesHigh * TILE);
    // zoom inteiro: cada pixel da arte vira um bloco exato de pixels da tela
    const zoom = Math.max(1, Math.round(ideal));
    const cam = this.cameras.main;
    cam.setViewport(0, 0, L.width, viewH);
    cam.setZoom(zoom);
    this.lookAhead = (L.portrait ? 36 : 28) * U;
    this.game.events.emit('layout');
  }

  setupKeyboard() {
    const kb = this.input.keyboard;
    this.keys = kb.addKeys({
      left: 'LEFT', right: 'RIGHT', up: 'UP', a: 'A', d: 'D', w: 'W', space: 'SPACE', z: 'Z',
      shift: 'SHIFT', x: 'X',
    });
  }

  // ---------- loop ----------

  update(time, delta) {
    if (this.state === 'playing') {
      this.updatePlayer(time, delta);
      this.checkFall();
    } else if (this.state === 'over') {
      this.updateCrying();
    }
    this.updateEnemies();
    this.updateDog(delta);
    if (this.waves) this.drawWaves(time);
    const cam = this.cameras.main;
    cam.followOffset.x = Phaser.Math.Linear(cam.followOffset.x, -this.facing * this.lookAhead, 0.04);
  }

  readInput() {
    const k = this.keys;
    return {
      left: k.left.isDown || k.a.isDown || touch.left,
      right: k.right.isDown || k.d.isDown || touch.right,
      jump: k.up.isDown || k.w.isDown || k.space.isDown || k.z.isDown || touch.jump,
      run: k.shift.isDown || k.x.isDown || touch.run,
    };
  }

  updatePlayer(time, delta) {
    const p = this.player;
    const body = p.body;
    const input = this.readInput();
    const onGround = body.blocked.down;
    const dt = delta / 16.67;

    if (onGround) this.lastGroundedAt = time;

    let dir = 0;
    if (input.left) dir -= 1;
    if (input.right) dir += 1;
    if (dir !== 0) this.facing = dir;

    const k = onGround ? PLAYER.accelGround : PLAYER.accelAir;
    const t = 1 - Math.pow(1 - k, dt);
    if (time > this.knockbackUntil) {
      body.setVelocityX(Phaser.Math.Linear(body.velocity.x, dir * (input.run ? PLAYER.runSpeed : PLAYER.speed), t));
    }

    // pulo com tolerancia de borda (coyote) e de antecipacao (buffer)
    if (input.jump && !this.prevJumpHeld) this.jumpPressedAt = time;
    const canJump = time - this.lastGroundedAt <= PLAYER.coyoteTime;
    if (time - this.jumpPressedAt <= PLAYER.jumpBuffer && canJump) {
      body.setVelocityY(-PLAYER.jumpVelocity);
      this.jumpPressedAt = -9999;
      this.lastGroundedAt = -9999;
    }
    if (body.velocity.y >= 0) this.molaBoost = false;
    // pulo curto ao soltar o botao (menos depois da mola, que lanca sempre com forca total)
    if (!input.jump && !this.molaBoost && body.velocity.y < -PLAYER.jumpCutVelocity) {
      body.setVelocityY(-PLAYER.jumpCutVelocity);
    }
    this.prevJumpHeld = input.jump;

    p.setFlipX(this.facing < 0);
    if (time < this.knockbackUntil + 150) p.play('raul-hurt', true);
    else if (!onGround) p.play(body.velocity.y < 0 ? 'raul-jump' : 'raul-fall', true);
    else if (Math.abs(body.velocity.x) > 12 * U) {
      p.play('raul-run', true);
      p.anims.timeScale = Math.abs(body.velocity.x) > PLAYER.speed + 10 * U ? 1.5 : 1;
    } else p.play('raul-idle', true);

    // guarda o checkpoint mais adiantado ja alcancado
    for (const c of this.checkpoints) {
      if (p.x >= c.x && c.x > this.respawnPoint.x && onGround) this.respawnPoint = { x: c.x, y: c.y };
    }
  }

  updateEnemies() {
    const t = this.time.now;
    this.enemies.children.each((e) => {
      if (!e.active || e.dead) return;
      const b = e.body;
      if (e.kind === 'floater') {
        const [ax, ay] = this.enemyDef.amp || [28, 26];
        e.setPosition(e.baseX + Math.sin(t / 1600 + e.phase) * ax * U, e.baseY + Math.sin(t / 650 + e.phase) * ay * U);
        const movingRight = Math.cos(t / 1600 + e.phase) > 0;
        e.setFlipX(this.enemyDef.faceRight ? !movingRight : movingRight);
        return;
      }
      if (b.blocked.left) e.dir = 1;
      else if (b.blocked.right) e.dir = -1;
      else if (b.blocked.down) {
        // vira antes de cair da borda
        const ahead = this.layer.getTileAtWorldXY(e.x + e.dir * 9 * U, b.bottom + 2 * U);
        if (!ahead || !ahead.collides) e.dir *= -1;
      }
      if (e.kind === 'bouncer' && b.blocked.down) {
        // amassa um instante e quica de novo
        e.anims.stop();
        e.setFrame(1);
        b.setVelocityY(-BOUNCE_V);
        this.time.delayedCall(90, () => e.active && !e.dead && e.play(`${this.enemyDef.key}-walk`, true));
      }
      e.setVelocityX(e.dir * ENEMY.speed * (e.kind === 'bouncer' ? 1.3 : 1));
      // espelha o desenho para olhar para onde anda
      e.setFlipX(this.enemyDef.faceRight ? e.dir < 0 : e.dir > 0);
    });
  }

  bounceMola(m) {
    const p = this.player.body;
    if (this.state !== 'playing' || p.velocity.y < 0 || p.bottom > m.body.top + 10 * U) return;
    p.setVelocityY(-PLAYER.jumpVelocity * MOLA_BOOST);
    this.molaBoost = true;
    this.lastGroundedAt = -9999;
    m.setFrame(1);
    this.time.delayedCall(160, () => m.setFrame(0));
  }

  updateDog(delta) {
    const p = this.player;
    const d = this.dog;
    const last = this.dogTrail[this.dogTrail.length - 1];
    if (!last || Math.abs(last.x - p.x) > 0.5 || Math.abs(last.y - p.y) > 0.5) {
      this.dogTrail.push({ x: p.x, y: p.y });
    }
    // o cachorro percorre o mesmo caminho do Raul, com atraso, mantendo distancia
    const far = Math.abs(d.x - p.x) > DOG.followGap || Math.abs(d.y - p.y) > 6 * U;
    let moved = false;
    if (far && this.dogTrail.length > 0) {
      const steps = this.dogTrail.length > 40 ? 2 : 1;
      for (let i = 0; i < steps && this.dogTrail.length; i++) {
        const pt = this.dogTrail.shift();
        if (pt.x !== d.x) d.setFlipX(pt.x < d.x);
        d.setPosition(pt.x, pt.y);
        moved = true;
      }
    }
    if (this.dogTrail.length > 120) this.dogTrail.splice(0, this.dogTrail.length - 120);

    if (moved) {
      this.dogIdleMs = 0;
      d.play('dog-run', true);
    } else {
      this.dogIdleMs += delta;
      if (Math.abs(p.x - d.x) > 2 * U) d.setFlipX(p.x < d.x);
      if (this.dogIdleMs > DOG.sleepAfter) d.play('dog-sleep', true);
      else if (this.dogIdleMs > DOG.sitAfter) d.play('dog-sit', true);
      else d.play('dog-stand', true);
    }
    const sleeping = this.dogIdleMs > DOG.sleepAfter;
    this.zzz.setVisible(sleeping);
    if (sleeping) {
      const tz = (this.time.now % 1500) / 1500;
      this.zzz.setPosition(d.x + (4 + tz * 4) * U, d.y - (14 + tz * 8) * U).setAlpha(1 - tz);
    }
  }

  drawWaves(time) {
    const cam = this.cameras.main;
    const g = this.waves.clear().fillStyle(0xffffff, 0.55);
    const x0 = Math.floor(cam.worldView.x / (8 * U)) * 8 * U;
    for (let x = x0; x < cam.worldView.right + 16 * U; x += 8 * U) {
      const h = Math.round((Math.sin(x / 40 + time / 300) + 1) * 2) * U;
      g.fillRect(x, this.waterTop - h, 8 * U, 2 * U);
    }
  }

  // ---------- eventos do jogo ----------

  collectCoin(c) {
    c.body.enable = false;
    this.coinCount += 1;
    this.tweens.killTweensOf(c);
    this.tweens.add({ targets: c, y: c.y - 14 * U, alpha: 0, scaleX: 1, duration: 260, onComplete: () => c.destroy() });
    this.emitHud();
  }

  touchEnemy(e) {
    if (e.dead || this.state !== 'playing') return;
    const p = this.player.body;
    const stomp = p.velocity.y > 0 && p.bottom <= e.body.top + 6 * U;
    if (stomp) {
      e.dead = true;
      e.anims.stop();
      e.setFrame(2);
      e.body.enable = false;
      this.player.body.setVelocityY(-PLAYER.stompBounce);
      this.lastGroundedAt = -9999;
      this.tweens.add({ targets: e, alpha: 0, delay: 350, duration: 250, onComplete: () => e.destroy() });
      this.cameras.main.shake(80, 0.004);
    } else {
      this.hurt(Math.sign(this.player.x - e.x) || 1);
    }
  }

  hurt(knockDir = 0) {
    if (this.time.now < this.invulnerableUntil) return false;
    this.hearts -= 1;
    this.emitHud();
    if (this.hearts <= 0) {
      this.gameOver();
      if (knockDir) this.player.body.setVelocity(knockDir * 60 * U, -120 * U);
      return true;
    }
    this.invulnerableUntil = this.time.now + PLAYER.invulnerableMs;
    if (knockDir) {
      this.player.body.setVelocity(knockDir * 150 * U, -200 * U);
      this.knockbackUntil = this.time.now + 220;
    }
    this.cameras.main.shake(120, 0.006);
    this.tweens.add({
      targets: this.player, alpha: 0.25, duration: 90, yoyo: true,
      repeat: Math.floor(PLAYER.invulnerableMs / 180) - 1,
      onComplete: () => this.player.setAlpha(1),
    });
    return true;
  }

  checkFall() {
    if (this.player.y < this.levelH + 24 * U) return;
    this.invulnerableUntil = 0;
    this.hurt();
    // volta para o ultimo ponto seguro; se acabaram os coracoes, ele chora la
    const r = this.respawnPoint;
    this.player.body.reset(r.x, r.y);
    this.dog.setPosition(r.x - DOG.followGap, r.y);
    this.dogTrail.length = 0;
    this.cameras.main.centerOn(r.x, r.y);
  }

  reachFlag() {
    if (this.state !== 'playing') return;
    this.state = 'won';
    const p = this.player;
    p.body.setVelocityX(0);
    p.play('raul-jump');
    this.tweens.add({ targets: p, y: p.y - 10 * U, duration: 220, yoyo: true, repeat: 3, ease: 'Quad.out' });
    const best = this.saveBest();
    this.game.events.emit('level-complete', { coins: this.coinCount, total: this.totalCoins(), best });
  }

  saveBest() {
    // recorde de moedas por fase, guardado neste aparelho
    const key = `raul-best-${this.level.id}`;
    let best = 0;
    try {
      best = Number(localStorage.getItem(key)) || 0;
      if (this.coinCount > best) localStorage.setItem(key, String(this.coinCount));
    } catch {
      // modo privado sem armazenamento: so nao guarda
    }
    return Math.max(best, this.coinCount);
  }

  totalCoins() {
    return this.rows.join('').split('o').length - 1;
  }

  // Sem morte: quando acabam os coracoes, o Raul senta no chao e chora.
  gameOver() {
    this.state = 'over';
    this.cryStarted = false;
    this.tweens.killTweensOf(this.player);
    this.player.setAlpha(1);
    this.player.play('raul-hurt');
  }

  updateCrying() {
    const p = this.player;
    const body = p.body;
    if (this.cryStarted) return;
    body.setVelocityX(body.velocity.x * 0.85);
    if (!body.blocked.down) return; // espera tocar o chao
    this.cryStarted = true;
    body.setVelocityX(0);
    p.play('raul-cry');
    this.game.events.emit('game-over');
  }

  emitHud() {
    this.game.events.emit('hud', { hearts: this.hearts, max: PLAYER.maxHearts, coins: this.coinCount });
  }
}
