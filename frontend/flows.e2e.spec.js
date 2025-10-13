// E2E: register -> logout -> login
//       events create/toggle/detail/toggle/delete
//       announcements create/delete
//       chat send/delete
//       profile set birthday/save

import { test, expect } from '@playwright/test';

const unique = Date.now().toString();
const username = `e2e_${unique}`;
const password = 'P@ssw0rd!';
const announceText = `E2Eお知らせ ${unique}`;
const chatText = `E2Eチャット ${unique}`;
const eventTitle = `E2Eイベント ${unique}`;

// Run serially so that we can keep session and data ordering
test.describe.configure({ mode: 'serial' });

test('01) / -> redirect to /login -> register -> logout -> login', async ({ page }) => {
  // Access root -> should redirect to /login
  await page.goto('/');
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole('heading', { name: 'ログイン' })).toBeVisible();

  // Go to register
  await page.getByRole('link', { name: 'ユーザー登録' }).click();
  await expect(page.getByRole('heading', { name: 'ユーザー登録' })).toBeVisible();

  // Register
  await page.getByPlaceholder('ユーザー名').fill(username);
  await page.getByPlaceholder('パスワード').fill(password);
  await page.getByRole('button', { name: '登録してログイン' }).click();

  // Land on dashboard
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole('heading', { name: '今週のイベント' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '最新のお知らせ' })).toBeVisible();

  // Logout
  await page.getByRole('link', { name: 'MyPage' }).click();
  await expect(page.getByRole('heading', { name: 'マイページ' })).toBeVisible();
  await page.getByRole('button', { name: 'ログアウト' }).click();
  await expect(page).toHaveURL(/\/login$/);

  // Re-login
  await page.getByPlaceholder('ユーザー名').fill(username);
  await page.getByPlaceholder('パスワード').fill(password);
  await page.getByRole('button', { name: 'ログイン' }).click();
  await expect(page).toHaveURL(/\/$/);
});

test('02) Events: create -> (toggle) -> detail -> (toggle) -> delete', async ({ page }) => {
  // Go to Events
  await page.getByRole('link', { name: 'Events' }).click();
  await expect(page.getByRole('heading', { name: 'イベント一覧' })).toBeVisible();

  // Fill create form
  await page.getByPlaceholder('例: FLARE ミートアップ').fill(eventTitle);

  const toLocalDatetime = (d) => {
    // YYYY-MM-DDTHH:mm
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };
  const start = new Date(Date.now() + 60*60*1000);
  const end = new Date(Date.now() + 2*60*60*1000);

  await page.locator('label:has-text("開始日時") + input[type="datetime-local"]').fill(toLocalDatetime(start));
  await page.locator('label:has-text("終了日時") + input[type="datetime-local"]').fill(toLocalDatetime(end));
  await page.getByRole('button', { name: '作成' }).click();

  // Wait for the new event card
  const wrapper = page.locator('.card', { hasText: eventTitle }).first();
  await expect(wrapper).toBeVisible();

  // Toggle attendance in list
  await wrapper.getByRole('button', { name: '参加表明' }).click();
  await expect(wrapper.getByRole('button', { name: '参加取消' })).toBeVisible();

  // Open detail page
  await wrapper.getByRole('link', { name: '詳細' }).click();
  await expect(page.getByRole('heading', { name: eventTitle })).toBeVisible();

  // Toggle on detail
  const toggleBtn = page.getByRole('button', { name: /参加取消|参加表明/ });
  const currentLabel = await toggleBtn.innerText();
  await toggleBtn.click();
  const expectedNext = currentLabel.trim() === '参加取消' ? '参加表明' : '参加取消';
  await expect(page.getByRole('button', { name: expectedNext })).toBeVisible();

  // Back to list
  await page.getByRole('link', { name: 'Events' }).click();
  await expect(page.getByRole('heading', { name: 'イベント一覧' })).toBeVisible();

  // Delete the event (accept confirm)
  page.once('dialog', d => d.accept());
  await page.locator('.card', { hasText: eventTitle }).first().getByRole('button', { name: '削除' }).click();

  // Ensure gone
  await expect(page.getByText(eventTitle)).toHaveCount(0);
});

test('03) Announcements: create -> delete', async ({ page }) => {
  await page.getByRole('link', { name: 'News' }).click();
  await expect(page.getByRole('heading', { name: 'お知らせ' })).toBeVisible();

  await page.getByPlaceholder('お知らせ内容').fill(announceText);
  await page.getByRole('button', { name: '投稿' }).click();

  const item = page.locator('.card', { hasText: announceText }).first();
  await expect(item).toBeVisible();

  page.once('dialog', d => d.accept());
  // In Announcements.vue the remove is a <button> labelled "削除"
  await item.getByRole('button', { name: '削除' }).click();

  await expect(page.getByText(announceText)).toHaveCount(0);
});

test('04) Chat: send -> delete', async ({ page }) => {
  await page.getByRole('link', { name: 'Chat' }).click();
  await expect(page.getByRole('heading', { name: 'コミュニティチャット' })).toBeVisible();

  await page.getByPlaceholder('メッセージを入力...').fill(chatText);
  await page.getByRole('button', { name: '送信' }).click();

  const bubble = page.locator('.chat-bubble', { hasText: chatText }).first();
  await expect(bubble).toBeVisible();

  page.once('dialog', d => d.accept());
  // "削除" is an anchor inside the bubble for own messages
  await bubble.getByText('削除').click();
  await expect(page.getByText(chatText)).toHaveCount(0);
});

test('05) Profile: set birthday -> save', async ({ page }) => {
  await page.getByRole('link', { name: 'MyPage' }).click();
  await expect(page.getByRole('heading', { name: 'マイページ' })).toBeVisible();

  const date = '1990-01-02';
  await page.locator('input[type="date"]').fill(date);
  await page.getByRole('button', { name: '保存' }).click();

  // Confirm the value remains (and save succeeded)
  await expect(page.locator('input[type="date"]')).toHaveValue(date);
});
