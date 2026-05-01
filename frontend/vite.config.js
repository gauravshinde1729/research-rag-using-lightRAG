import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy /api → FastAPI on :8000 so the browser thinks the API is same-origin
// and we don't need CORS gymnastics in dev.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
