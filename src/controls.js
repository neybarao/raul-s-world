// Estado de entrada compartilhado entre a cena do jogo e a cena da interface.
// A UIScene escreve (toque), a GameScene le e combina com o teclado.
export const touch = { left: false, right: false, jump: false, run: false };

// Layout calculado no resize e compartilhado entre as cenas.
export const layout = {
  width: 0,
  height: 0,
  portrait: false,
  hasTouch: false,
  controlsHeight: 0, // faixa de botoes embaixo no modo em pe
  dpr: 1, // pixels fisicos por pixel CSS (todas as medidas acima estao em pixels fisicos)
};

export function computeLayout(game) {
  const { width, height } = game.scale.gameSize;
  const hasTouch = game.device.input.touch;
  const portrait = height > width;
  const dpr = game.canvas && game.canvas.clientWidth ? width / game.canvas.clientWidth : 1;
  layout.dpr = dpr;
  layout.width = width;
  layout.height = height;
  layout.portrait = portrait;
  layout.hasTouch = hasTouch;
  layout.controlsHeight = portrait && hasTouch ? Math.round(Math.min(height * 0.32, 280 * dpr)) : 0;
  return layout;
}
