import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:4201/web/index.php/auth/login';
const USERNAME = 'Admin';
const PASSWORD = 'Admin@123098'; // Change to 'admin123' if your DB uses that

test('Update employee job details', async ({ page }) => {
  // 1. Open login page directly
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });

  // 2. Login
  await page.locator("input[name='username']").fill(USERNAME);
  await page.locator("input[name='password']").fill(PASSWORD);
  await page.locator("button[type='submit']").click();

  // Confirm dashboard is reached
  await expect(page).toHaveURL(/.*dashboard\/index.*/, { timeout: 30000 });

  // 3. Navigate to PIM
  await page.getByRole('link', { name: 'PIM' }).click();
  await page.waitForURL('**/pim/viewEmployeeList**');

  // 4. Open 'Test Employee' profile (avoiding the read-only Admin User row)
  const testEmployeeRow = page.locator('.oxd-table-row').filter({ hasText: 'Test Employee' }).first();
  await expect(testEmployeeRow).toBeVisible({ timeout: 15000 });
  await testEmployeeRow.click();

  // 5. Open Job tab
  const jobTab = page.getByRole('link', { name: 'Job' });
  await expect(jobTab).toBeVisible({ timeout: 10000 });
  await jobTab.click();
  await page.waitForURL('**/pim/viewJobDetails/empNumber/**');

  // 6. Select Job Title dropdown
  const jobTitleDropdown = page.locator('.oxd-select-text').first();
  await expect(jobTitleDropdown).toBeVisible({ timeout: 10000 });
  await jobTitleDropdown.click();

  // Select the configured job title (nth(1) after '-- Select --')
  const dropdownOption = page.locator('.oxd-select-dropdown .oxd-select-option').nth(1);
  await expect(dropdownOption).toBeVisible({ timeout: 5000 });
  await dropdownOption.click();

  // 7. Save job details without strict-mode collisions
  const saveButton = page.locator('form').filter({ hasText: 'Joined Date' }).getByRole('button', { name: 'Save' });
  if (await saveButton.isVisible()) {
    await saveButton.click();
  } else {
    await page.locator("button[type='submit']").first().click();
  }

  // 8. Verify success toast notification
  await expect(page.locator('.oxd-toast--success')).toBeVisible({ timeout: 10000 });

  // 9. Reload and verify selected value persisted
  await page.reload({ waitUntil: 'networkidle' });
  await expect(page.locator('.oxd-select-text').first()).not.toHaveText('-- Select --');
});