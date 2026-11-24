// Ajustes de jogabilidade em um lugar so, para facilitar o balanceamento.
export const TILE = 16;

export const PLAYER = {
  speed: 105,
  runSpeed: 165, // segurando B (ou Shift/X no teclado)
  accelGround: 0.28,
  accelAir: 0.14,
  jumpVelocity: 335,
  jumpCutVelocity: 130, // ao soltar o botao cedo, o pulo fica mais baixo
  coyoteTime: 100, // ms em que ainda da pra pular depois de sair da borda
  jumpBuffer: 120, // ms em que um toque antes de aterrissar ainda vale
  stompBounce: 240,
  maxHearts: 3,
  invulnerableMs: 1400,
};

export const ENEMY = { speed: 28 };

export const DOG = {
  followGap: 18, // distancia em px que o cachorro mantem do Raul
  sitAfter: 1200,
  sleepAfter: 6000,
};

// Quantos blocos de largura aparecem no celular em pe,
// e quantos de altura no modo deitado/computador.
export const VIEW = { portraitTilesWide: 11, landscapeTilesHigh: 15 };

export const SKY = '#5aa8e8';
