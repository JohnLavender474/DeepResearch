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
    port: 5173,
    host: '0.0.0.0',
    watch: {
      usePolling: true,
    },
    hmr: {
      host: 'localhost',
      port: 8004,
    },
    proxy: {
      '/api/embeddings': {
        target: 'http://embedding_service:8000',
        changeOrigin: true
      },
      '/api/graph': {
        target: 'http://graph_service:8001',
        changeOrigin: true
      },
      '/api/storage': {
        target: 'http://storage_service:8002',
        changeOrigin: true
      }, 
      '/api/database': {
        target: 'http://database_service:8003',
        changeOrigin: true
      }    
    }
  }
})
