import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/approvals': 'http://127.0.0.1:8000',
      '/audit': 'http://127.0.0.1:8000',
      '/metrics': 'http://127.0.0.1:8000',
      '/stats': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    },
  },
})
