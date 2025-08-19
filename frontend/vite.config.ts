import { defineConfig } from 'vite';

export default defineConfig({
  optimizeDeps: {
    exclude: ['chunk-EQ65KABV'] // Añade aquí el nombre del chunk problemático
  }
});