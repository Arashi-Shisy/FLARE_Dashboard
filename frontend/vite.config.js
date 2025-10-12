import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vitest は Vite の設定ファイルから test オプションを読み取ります
export default defineConfig({
  plugins: [vue()],
  server: { port: 5173, host: true },
  build: { outDir: 'dist' },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./test/setup.js'],
    css: true,
    coverage: {
      reporter: ['text', 'html'],
      reportsDirectory: './coverage',
    }
  }
})
