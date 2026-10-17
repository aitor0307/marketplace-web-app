import path from 'node:path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  // With VITE_API_URL unset the app calls the API same-origin; in dev the
  // proxy forwards those calls (and uploaded images) to the Flask server.
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://localhost:4000';

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      // Chakra UI v2 alone is ~520 kB minified (~170 kB gzip).
      chunkSizeWarningLimit: 600,
      rollupOptions: {
        output: {
          // Long-lived vendor chunks: app deploys don't bust the UI kit's cache.
          manualChunks: {
            react: ['react', 'react-dom', 'react-router-dom'],
            ui: ['@chakra-ui/react', '@emotion/react', '@emotion/styled', 'framer-motion'],
            data: [
              '@tanstack/react-query',
              'zustand',
              'i18next',
              'react-i18next',
              'react-hook-form',
            ],
          },
        },
      },
    },
    server: {
      port: 5173,
      host: true,
      proxy: {
        '/api': { target: proxyTarget, changeOrigin: true },
        '/static': { target: proxyTarget, changeOrigin: true },
      },
    },
  };
});
