// PWA: instala o service worker, procura atualizacoes e entra em tela cheia.
const CHECK_EVERY_MS = 5 * 60 * 1000;
let reloading = false;

function showToastAndReload() {
  if (reloading) return;
  reloading = true;
  document.getElementById('update-toast')?.classList.add('show');
  setTimeout(() => window.location.reload(), 1400);
}

// Compara a versao publicada (version.json, sem cache) com a versao que esta rodando.
async function checkForUpdate(reg) {
  let build;
  try {
    const res = await fetch(`./version.json?t=${Date.now()}`, { cache: 'no-store' });
    if (!res.ok) return;
    ({ build } = await res.json());
  } catch {
    return; // sem internet: segue jogando a versao em cache
  }
  if (!build || build === __BUILD_ID__) return;
  // garante a recarga mesmo se o service worker falhar ou demorar
  setTimeout(showToastAndReload, reg ? 3000 : 0);
  if (reg) reg.update().catch(() => {});
}

export function setupPWA() {
  if (import.meta.env.DEV) return;
  let reg = null;
  if ('serviceWorker' in navigator) {
    const hadController = !!navigator.serviceWorker.controller;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      // um service worker novo assumiu: era uma atualizacao (nao a primeira instalacao)
      if (hadController) showToastAndReload();
    });
    navigator.serviceWorker.register('./sw.js').then((r) => {
      reg = r;
      checkForUpdate(reg);
    });
  } else {
    checkForUpdate(null);
  }
  // procura de novo ao voltar para o app e de tempos em tempos
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') checkForUpdate(reg);
  });
  setInterval(() => checkForUpdate(reg), CHECK_EVERY_MS);
}

// No navegador (fora do app instalado), entra em tela cheia no primeiro toque onde der.
// O iPhone nao permite tela cheia em pagina; la a tela cheia vem ao adicionar a Tela de Inicio.
export function setupFullscreen() {
  const standalone = window.matchMedia('(display-mode: fullscreen), (display-mode: standalone)').matches || navigator.standalone;
  const el = document.documentElement;
  if (standalone || !el.requestFullscreen || !('ontouchstart' in window)) return;
  const go = () => {
    if (!document.fullscreenElement) el.requestFullscreen({ navigationUI: 'hide' }).catch(() => {});
  };
  window.addEventListener('pointerup', go, { once: true });
}
