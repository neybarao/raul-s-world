// Ajustes de jogabilidade em um lugar so, para facilitar o balanceamento.
// Escala 32 bits: blocos de 32 px. U converte medidas pensadas em 16 px.
export const TILE = 32;
export const U = TILE / 16;
export const GRAVITY = 900 * U;

export const PLAYER = {
  speed: 105 * U,
  runSpeed: 165 * U, // segurando B (ou Shift/X no teclado)
  accelGround: 0.28,
  accelAir: 0.14,
  jumpVelocity: 335 * U,
  jumpCutVelocity: 130 * U, // ao soltar o botao cedo, o pulo fica mais baixo
  coyoteTime: 100, // ms em que ainda da pra pular depois de sair da borda
  jumpBuffer: 120, // ms em que um toque antes de aterrissar ainda vale
  stompBounce: 240 * U,
  maxHearts: 3,
  invulnerableMs: 1400,
};

export const ENEMY = { speed: 28 * U };

// bolinhas de piscina arremessadas com o botao B (ou X no teclado)
export const BALL = {
  speedX: 290 * U, // velocidade para frente (soma metade da velocidade do Raul)
  speedY: 25 * U, // so um toque para cima: o arremesso vai reto para frente, quase sem arco
  bounce: 0.55, // quanto quica no chao (vai pulando baixinho rente ao chao)
  lifeMs: 1400, // some depois desse tempo
  max: 3, // quantas podem estar no ar ao mesmo tempo
  cooldownMs: 300, // intervalo minimo entre dois arremessos
  windupMs: 70, // quanto tempo o Raul fica na pose de preparar antes de soltar
  poseMs: 260, // duracao total da pose de arremesso
  aimRange: 9 * TILE, // mira automatica: bicho a frente ate essa distancia
  aimAbove: 3 * TILE, // ... e no maximo isso acima da mao
  aimBelow: 2 * TILE, // ... ou isso abaixo
  maxAimSpeedY: 260 * U, // limite da inclinacao da mira
};

export const DOG = {
  followGap: 22 * U, // distancia em px que o cachorro mantem do Raul
  sitAfter: 1200,
  sleepAfter: 6000,
};

// Quantos blocos de largura aparecem no celular em pe,
// e quantos de altura no modo deitado/computador.
export const VIEW = { portraitTilesWide: 11, landscapeTilesHigh: 15 };

export const SKY = '#5aa8e8';
