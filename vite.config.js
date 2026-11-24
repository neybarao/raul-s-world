import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { defineConfig } from 'vite';

// identificador unico de cada build, usado para o navegador nunca reaproveitar arquivos antigos
const BUILD_ID = (process.env.GITHUB_SHA || String(Date.now())).slice(0, 10);

function listFiles(dir) {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? listFiles(full) : [full];
  });
}

// gera sw.js (service worker) e version.json com o id do build.
// O sw.js recebe a lista de TODOS os arquivos do jogo, para baixar tudo na instalacao
// e o jogo funcionar offline ja depois da primeira visita.
function pwaFiles() {
  return {
    name: 'pwa-files',
    apply: 'build',
    generateBundle(_options, bundle) {
      const publicDir = new URL('./public', import.meta.url).pathname;
      const publicFiles = listFiles(publicDir).map((f) => relative(publicDir, f).split('\\').join('/'));
      const urls = [
        './',
        ...Object.keys(bundle).filter((f) => !f.endsWith('.map')),
        // imagens e musicas sao pedidas pelo jogo com ?v=<build>; os icones e o manifesto, sem
        ...publicFiles.map((f) => (f.startsWith('assets/') ? `${f}?v=${BUILD_ID}` : f)),
      ];
      const sw = readFileSync(new URL('./src/sw-template.js', import.meta.url), 'utf8')
        .replaceAll('__BUILD_ID__', BUILD_ID)
        .replace('__PRECACHE__', JSON.stringify([...new Set(urls)]));
      this.emitFile({ type: 'asset', fileName: 'sw.js', source: sw });
      this.emitFile({ type: 'asset', fileName: 'version.json', source: JSON.stringify({ build: BUILD_ID }) });
    },
  };
}

// base relativo para funcionar no GitHub Pages (com ou sem dominio proprio)
export default defineConfig({
  base: './',
  define: { __BUILD_ID__: JSON.stringify(BUILD_ID) },
  plugins: [pwaFiles()],
  build: { chunkSizeWarningLimit: 2000 },
});
