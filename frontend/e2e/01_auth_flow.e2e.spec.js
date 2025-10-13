// / -> redirect -> register -> logout -> login
import { test, expect } from '@playwright/test';

const unique = Date.now().toString();
const username = `e2e_${unique}`;
const password = 'P@ssw0rd!';

test('01) / -> /login -> register -> logout -> login', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole('heading', { name: 'ログイン' })).toBeVisible();

  // register
  await page.getByRole('link', { name: 'ユーザー登録' }).click();
  await expect(page.getByRole('heading', { name: 'ユーザー登録' })).toBeVisible();
  await page.getByPlaceholder('ユーザー名').fill(username);
  await page.getByPlaceholder('パスワード').fill(password);
  await page.getByRole('button', { name: '登録してログイン' }).click();

  // land on dashboard
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole('heading', { name: '今週のイベント' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '最新のお知らせ' })).toBeVisible();

  // logout
  await page.click('a[href="/profile"]');
  await expect(page.getByRole('heading', { name: 'マイページ' })).toBeVisible();
  await page.getByRole('button', { name: 'ログアウト' }).click();
  await expect(page).toHaveURL(/\/login$/);

  // login
  await page.getByPlaceholder('ユーザー名').fill(username);
  await page.getByPlaceholder('パスワード').fill(password);
  await page.getByRole('button', { name: 'ログイン' }).click();
  await expect(page).toHaveURL(/\/$/);
});
