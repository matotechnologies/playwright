const { test, expect } = require('@playwright/test');

test('OrangeHRM valid admin login and dashboard validation', async ({ page }) => {
  // 1. Navigate to login route
  await page.goto('/web/index.php/auth/login', { waitUntil: 'networkidle' });

  // 2. Fill login credentials
  const usernameInput = page.locator("input[name='username']");
  const passwordInput = page.locator("input[name='password']");
  const submitButton = page.locator("button[type='submit']");

  await expect(usernameInput).toBeVisible({ timeout: 15000 });

  await usernameInput.fill('Admin');
  await passwordInput.fill('admin123');
  await submitButton.click();

  // 3. Confirm redirection to dashboard
  await expect(page).toHaveURL(/.*\/dashboard\/index.*/, { timeout: 30000 });

  // 4. Confirm dashboard header
  const dashboardHeader = page.locator('header h6');
  await expect(dashboardHeader).toBeVisible({ timeout: 10000 });
  await expect(dashboardHeader).toHaveText('Dashboard');
});