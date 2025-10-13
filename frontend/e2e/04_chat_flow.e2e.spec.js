// Chat: send -> delete
import { test, expect } from '@playwright/test';

const unique = Date.now().toString();
const chatText = `E2Eチャット ${unique}`;

test('04) Chat send/delete', async ({ page }) => {
  await page.goto('/chat');
  await expect(page.getByRole('heading', { name: 'コミュニティチャット' })).toBeVisible();

  await page.getByPlaceholder('メッセージを入力...').fill(chatText);
  await page.getByRole('button', { name: '送信' }).click();

  const bubble = page.locator('.chat-bubble', { hasText: chatText }).first();
  await expect(bubble).toBeVisible();

  page.once('dialog', d => d.accept());
  await bubble.getByText('削除').click();
  await expect(page.getByText(chatText)).toHaveCount(0);
});
