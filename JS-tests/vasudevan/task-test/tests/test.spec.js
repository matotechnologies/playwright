const { test, expect } = require('@playwright/test');

test('Toolshop frontend smoke test', async ({ page }) => {
  await page.goto('http://localhost:4200');
  await expect(page).toHaveTitle(/Practice Software Testing/i);
  
});
