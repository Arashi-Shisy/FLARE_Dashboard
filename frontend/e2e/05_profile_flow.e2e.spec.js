// Profile: set birthday -> save
import { test, expect } from '@playwright/test';

test('05) Profile set birthday -> save', async ({ page }) => {
  await page.goto('/profile');
  await expect(page.getByRole('heading', { name: 'マイページ' })).toBeVisible();

  const date = '1990-01-02';
  await page.locator('input[type="date"]').fill(date);
  await page.getByRole('button', { name: '保存' }).click();

  await expect(page.locator('input[type="date"]')).toHaveValue(date);
});
