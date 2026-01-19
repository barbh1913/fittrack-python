import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true
  },
  server: {
    proxy: {
      // Proxy API routes to Flask backend
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
