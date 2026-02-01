import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'


export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // Frontend dev server runs on port 8004 - 
    // this is where users access the UI
    port: 8004,
    host: '0.0.0.0',
    proxy: {
      // Proxy routes forward frontend requests to backend services.
      // The browser sees all requests as same-origin (port 8004),
      // which solves CORS issues. Example: fetch('/graph/...') 
      // is transparently forwarded to http://localhost:8001/graph/...
      '/embeddings': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/graph': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '/storage': {
        target: 'http://localhost:8002',
        changeOrigin: true
      }, 
      '/api/database': {
        target: 'http://localhost:8003',
        changeOrigin: true
      }    
    }
  }
})
