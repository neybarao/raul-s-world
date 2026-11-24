// Service worker do Raul's World. Gerado no build: __BUILD_ID__ muda a cada publicacao,
// entao o navegador percebe um arquivo novo, instala esta versao e descarta o cache antigo.
const VERSION = '__BUILD_ID__';
const CACHE = `raul-${VERSION}`;
// todos os arquivos do jogo (lista gerada no build): baixados na instalacao, para jogar offline
const PRECACHE = __PRECACHE__;

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  // arquivo de versao: sempre da rede, nunca do cache
  if (url.pathname.endsWith('/version.json')) return;

  // pagina: rede primeiro (pega atualizacoes), cache se estiver offline
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put('./index.html', copy));
          return res;
        })
        .catch(() => caches.match('./index.html', { ignoreVary: true }).then((r) => r || caches.match('./', { ignoreVary: true })))
    );
    return;
  }

  // codigo e imagens: tem hash ou ?v= no nome, entao cache primeiro e seguro
  event.respondWith(
    // ignoreVary: o arquivo foi guardado na instalacao, mas o jogo o pede como script/imagem
    // (cabecalhos diferentes); sem isso o cache nao reconhece e falha offline
    caches.match(req, { ignoreVary: true }).then((hit) =>
      hit ||
      fetch(req).then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      })
    )
  );
});
