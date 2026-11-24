import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
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
        // imagens, musicas, icones e manifesto sao pedidos com ?v=<build>
        ...publicFiles.map((f) => (/^(assets|icons)\/|\.webmanifest$/.test(f) ? `${f}?v=${BUILD_ID}` : f)),
      ];
      const sw = readFileSync(new URL('./src/sw-template.js', import.meta.url), 'utf8')
        .replaceAll('__BUILD_ID__', BUILD_ID)
        .replace('__PRECACHE__', JSON.stringify([...new Set(urls)]));
      this.emitFile({ type: 'asset', fileName: 'sw.js', source: sw });
      this.emitFile({ type: 'asset', fileName: 'version.json', source: JSON.stringify({ build: BUILD_ID }) });
    },
    // o iPhone guarda o icone pelo endereco: com ?v=<build> cada versao tem endereco novo
    transformIndexHtml(html) {
      return html.replace(/href="(\.\/(?:icons\/[^"]+|manifest\.webmanifest))"/g, `href="$1?v=${BUILD_ID}"`);
    },
    closeBundle() {
      const out = new URL('./dist/manifest.webmanifest', import.meta.url).pathname;
      const m = JSON.parse(readFileSync(out, 'utf8'));
      m.icons = m.icons.map((i) => ({ ...i, src: `${i.src}?v=${BUILD_ID}` }));
      writeFileSync(out, JSON.stringify(m, null, 2));
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
