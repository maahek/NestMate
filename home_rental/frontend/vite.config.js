import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // ── REST API ────────────────────────────────────────────────────────
      '/api': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/media': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/accounts': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/roommate': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/agreements': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/analytics': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      // ── Chat API endpoints only (NOT React routes) ──────────────────────
      // Only proxy specific API paths, not /chat/<roomId> React routes
      '/chat/api': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/chat/start': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      // Proxy /chat/<id>/messages, /chat/<id>/mark-read, /chat/<id>/close
      // but NOT /chat/<id> alone (that's the React page)
      '/chat/6': {
        target:       'http://127.0.0.1:8000',
        changeOrigin: true,
        // Only forward if path has a second segment
        bypass(req) {
          const parts = req.url.split('/').filter(Boolean)
          // /chat/<id> alone → React page, don't proxy
          if (parts.length === 2) return req.url
          // /chat/<id>/messages/ etc → proxy to Django
          return null
        },
      },

      // ── WebSocket ───────────────────────────────────────────────────────
      // Use 127.0.0.1 NOT localhost — fixes ECONNREFUSED on Windows
      '/ws': {
        target:       'ws://127.0.0.1:8000',
        ws:            true,
        changeOrigin:  true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})