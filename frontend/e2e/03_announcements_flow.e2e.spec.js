// Announcements: create -> delete
import { test, expect } from '@playwright/test';

const unique = Date.now().toString();
const announceText = `E2Eお知らせ ${unique}`;

test('03) Announcements create/delete', async ({ page }) => {
  await page.goto('/announcements');
  await expect(page.getByRole('heading', { name: 'お知らせ' })).toBeVisible();

  await page.getByPlaceholder('お知らせ内容').fill(announceText);
  await page.getByRole('button', { name: '投稿' }).click();

  const item = page.locator('.card', { hasText: announceText }).first();
  await expect(item).toBeVisible();

  page.once('dialog', d => d.accept());
  await item.getByRole('button', { name: '削除' }).click();

  await expect(page.getByText(announceText)).toHaveCount(0);
});
