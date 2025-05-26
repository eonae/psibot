import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/dev/telegram_miniapp',
  plugins: [react()],
  server: {
    host: true,
    allowedHosts: ['eonae.dev', 'localhost'],
  },
})
