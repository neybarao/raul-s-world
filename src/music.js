// Musica de fundo: uma trilha por vez, em loop, com liga/desliga guardado no aparelho.
// Usa o gerenciador de som global do jogo (sobrevive a troca de cenas).
const VOLUME = 0.55;
const VOLUME_PAUSED = 0.18;

let current = null; // { key, sound }
let paused = false;

function readMuted() {
  try {
    return localStorage.getItem('raul-som') === 'off';
  } catch {
    return false;
  }
}

let muted = readMuted();

export const isMuted = () => muted;

function targetVolume() {
  if (muted) return 0;
  return paused ? VOLUME_PAUSED : VOLUME;
}

export function playMusic(scene, key) {
  const sm = scene.sound;
  if (!key || !scene.cache.audio.exists(key)) return;
  if (current && current.key === key) {
    current.sound.setVolume(targetVolume());
    return;
  }
  if (current) {
    current.sound.stop();
    current.sound.destroy();
  }
  const sound = sm.add(key, { loop: true, volume: targetVolume() });
  current = { key, sound };
  // no celular o navegador so libera audio depois do primeiro toque
  if (sm.locked) sm.once('unlocked', () => current && current.sound === sound && sound.play());
  else sound.play();
}

export function setMusicPaused(value) {
  paused = value;
  if (current) current.sound.setVolume(targetVolume());
}

export function toggleMute() {
  muted = !muted;
  try {
    localStorage.setItem('raul-som', muted ? 'off' : 'on');
  } catch {
    // sem armazenamento: vale so ate fechar
  }
  if (current) current.sound.setVolume(targetVolume());
  return muted;
}

// para testes e depuracao
export const musicState = () => ({
  key: current?.key || null,
  playing: !!current?.sound.isPlaying,
  volume: current ? Math.round(current.sound.volume * 100) / 100 : null,
  muted,
  paused,
});
