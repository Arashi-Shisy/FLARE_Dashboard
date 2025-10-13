// Events: create -> toggle -> detail -> toggle -> delete
import { test, expect } from '@playwright/test';

const unique = Date.now().toString();
const eventTitle = `E2Eイベント ${unique}`;

function toLocalDatetime(d) {
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

test('02) Events CRUD + attend toggle (list/detail)', async ({ page }) => {
  await page.goto('/events');
  await expect(page.getByRole('heading', { name: 'イベント一覧' })).toBeVisible();

  // Create
  await page.getByPlaceholder('例: FLARE ミートアップ').fill(eventTitle);
  const start = new Date(Date.now() + 60*60*1000);
  const end = new Date(Date.now() + 2*60*60*1000);
  const startInput = page.locator('label:has-text("開始日時") + input[type="datetime-local"], input[type="datetime-local"]').first();
  const endInput = page.locator('label:has-text("終了日時") + input[type="datetime-local"], input[type="datetime-local"]').nth(1);
  await startInput.fill(toLocalDatetime(start));
  await endInput.fill(toLocalDatetime(end));
  await page.getByRole('button', { name: '作成' }).click();

  const card = page.locator('.card', { hasText: eventTitle }).first();
  await expect(card).toBeVisible();

  // Toggle in list
  const toggleBtn = card.getByRole('button', { name: /参加表明|参加取消/ });
  const firstLabel = (await toggleBtn.innerText()).trim();
  await toggleBtn.click();
  const nextLabel = firstLabel === '参加取消' ? '参加表明' : '参加取消';
  await expect(card.getByRole('button', { name: nextLabel })).toBeVisible();

  // Detail
  await card.getByRole('link', { name: '詳細' }).click();
  await expect(page.getByRole('heading', { name: eventTitle })).toBeVisible();

  const dToggle = page.getByRole('button', { name: /参加表明|参加取消/ });
  const dLabel = (await dToggle.innerText()).trim();
  await dToggle.click();
  const dNext = dLabel === '参加取消' ? '参加表明' : '参加取消';
  await expect(page.getByRole('button', { name: dNext })).toBeVisible();

  // Back to list
  await page.click('a[href="/events"]');
  await expect(page.getByRole('heading', { name: 'イベント一覧' })).toBeVisible();

  // Delete
  const row = page.locator('.card', { hasText: eventTitle }).first();
  await expect(row).toBeVisible();
  page.once('dialog', d => d.accept());
  await row.getByRole('button', { name: '削除' }).click();
  await expect(page.getByText(eventTitle)).toHaveCount(0);
});
