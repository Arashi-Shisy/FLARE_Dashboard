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
  projects: [
    // 1) Setup: login once and write storage to e2e/.auth/user.json
    {
      name: 'setup',
      testMatch: ['e2e/setup/auth.setup.e2e.js'],
      use: { ...devices['Desktop Chrome'], storageState: undefined },
    },
    // 2) Main: reuse saved auth for all scenario tests
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'e2e/.auth/user.json',
      },
      dependencies: ['setup'],
      testIgnore: ['e2e/setup/**', 'e2e/01_auth_flow.e2e.spec.js'], // auth-flow runs without storage
    },
    // 3) Auth-flow project: explicitly start without storage state
    {
      name: 'auth-flow',
      use: {
        ...devices['Desktop Chrome'],
        storageState: undefined,
      },
      testMatch: ['e2e/01_auth_flow.e2e.spec.js'],
      dependencies: ['setup'], // keep order predictable (optional)
    },
  ],
});
