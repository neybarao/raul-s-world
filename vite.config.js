import { defineConfig } from 'vite';

// identificador unico de cada build, usado para o navegador nunca reaproveitar imagens antigas
const BUILD_ID = (process.env.GITHUB_SHA || String(Date.now())).slice(0, 10);

// base relativo para funcionar no GitHub Pages (com ou sem dominio proprio)
export default defineConfig({
  base: './',
  define: { __BUILD_ID__: JSON.stringify(BUILD_ID) },
  build: { chunkSizeWarningLimit: 2000 },
});
