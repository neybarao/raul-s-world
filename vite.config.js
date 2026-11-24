import { readFileSync } from 'node:fs';
import { defineConfig } from 'vite';

// identificador unico de cada build, usado para o navegador nunca reaproveitar arquivos antigos
const BUILD_ID = (process.env.GITHUB_SHA || String(Date.now())).slice(0, 10);

// gera sw.js (service worker) e version.json com o id do build
function pwaFiles() {
  return {
    name: 'pwa-files',
    apply: 'build',
    generateBundle() {
      const sw = readFileSync(new URL('./src/sw-template.js', import.meta.url), 'utf8').replaceAll('__BUILD_ID__', BUILD_ID);
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
