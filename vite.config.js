import { defineConfig } from 'vite';

// base relativo para funcionar em https://neybarao.github.io/raul-s-world/
export default defineConfig({
  base: './',
  build: { chunkSizeWarningLimit: 2000 },
});
