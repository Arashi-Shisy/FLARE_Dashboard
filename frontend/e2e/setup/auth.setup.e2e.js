// Runs once to create an account and persist login state for the suite.
import { test, expect } from '@playwright/test';
import fs from 'fs';

const unique = Date.now().toString();
const username = `e2e_user_${unique}`;
const password = 'P@ssw0rd!';

test('setup: register and save storageState', async ({ page, context }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/login$/);
  await page.getByRole('link', { name: 'ユーザー登録' }).click();
  await expect(page.getByRole('heading', { name: 'ユーザー登録' })).toBeVisible();

  await page.getByPlaceholder('ユーザー名').fill(username);
  await page.getByPlaceholder('パスワード').fill(password);
  await page.getByRole('button', { name: '登録してログイン' }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole('heading', { name: '今週のイベント' })).toBeVisible();

  await context.storageState({ path: 'e2e/.auth/user.json' });
  fs.writeFileSync('e2e/.auth/creds.json', JSON.stringify({ username, password }, null, 2));
});
