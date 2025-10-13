/**
 * Playwright config for FLARE Dashboard E2E.
 * Expects the app to be running at BASE_URL (default http://localhost:8080).
 */
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e',                              // ← E2E専用ディレクトリだけを見る
  testMatch: ['**/*.e2e.spec.{js,ts}'],        // ← E2E用の拡張子に限定（おすすめ）
  testIgnore: ['**/__tests__/**', '**/src/**'],// ← 念のためユニット側は無視
  fullyParallel: true,
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8080',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
