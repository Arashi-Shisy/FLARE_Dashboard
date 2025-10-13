import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e',
  testMatch: ['**/*.e2e.spec.{js,ts}'],
  testIgnore: ['**/__tests__/**', 'test/**', '**/src/**'],
  fullyParallel: false,
  retries: 0,
  reporter: [['html', { outputFolder: 'playwright-report', open: 'never' }]],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8080',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  // Put main projects first so UI mode shows them by default
  projects: [
    // Main (logged-in) tests reuse storageState
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
      testIgnore: ['e2e/setup/**', 'e2e/01_auth_flow.e2e.spec.js'],
    },
    // Auth-flow (unauthenticated) runs without storage
    {
      name: 'auth-flow',
      use: { ...devices['Desktop Chrome'], storageState: undefined },
      testMatch: ['e2e/01_auth_flow.e2e.spec.js'],
      dependencies: ['setup'],
    },
    // Setup: logs in once and saves storageState
    {
      name: 'setup',
      testMatch: ['e2e/setup/auth.setup.e2e.js'],
      use: { ...devices['Desktop Chrome'], storageState: undefined },
    },
  ],
});
