import { test, expect } from '@playwright/test';

test('index -> redirect to login -> go to register -> register user', async ({ page }) => {
  // 1) Access index; should land on login due to router guard
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'ログイン' })).toBeVisible();

  // 2) Go to register page
  await page.getByRole('link', { name: 'ユーザー登録' }).click();
  await expect(page.getByRole('heading', { name: 'ユーザー登録' })).toBeVisible();

  // 3) Fill form and register
  const uname = `e2e_${Date.now()}_${Math.floor(Math.random()*1000)}`;
  await page.getByPlaceholder('ユーザー名').fill(uname);
  await page.getByPlaceholder('パスワード').fill('testpass123');
  await page.getByRole('button', { name: '登録してログイン' }).click();

  // 4) After registration, we should be redirected to Dashboard ('/')
  await expect(page).toHaveURL(/\/$/);
 // ページの追加リクエストが落ち着くまで待つ（初回描画＆API待ちのブレを吸収）
  await page.waitForLoadState('networkidle');
 // セマンティックでない見出しでも拾えるようにテキストベースでチェック
  await expect(page.getByText('今週のイベント', { exact: false })).toBeVisible({ timeout: 15000 });
  await expect(page.getByText('最新のお知らせ', { exact: false })).toBeVisible({ timeout: 15000 });
});
