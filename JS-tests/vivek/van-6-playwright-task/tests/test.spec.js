import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:4201';
const USERNAME = 'Admin';
const PASSWORD = 'Admin@123098';

test('Update employee job category', async ({ page }) => {

    // 1. Open OrangeHRM
    await page.goto(BASE_URL);

    // 2. Login to OrangeHRM
    await page.getByPlaceholder('Username').fill(USERNAME);
    await page.getByPlaceholder('Password').fill(PASSWORD);
    await page.getByRole('button', { name: 'Login' }).click();

    // 3. Navigate to PIM
    await page.getByRole('link', { name: 'PIM' }).click();

    // 4. Navigate to Employee List
    await page.getByText('Employee List', { exact: true }).click();

    // 5. Search for employee using Employee ID
    await page.locator('input').nth(1).fill('001');
    await page.getByRole('button', { name: 'Search' }).click();

    // 6. Open the employee profile
    await page.getByRole('row', { name: '001 Test Employee' }).click();

    // 7. Open the Job section
    await page.getByRole('link', { name: 'Job' }).click();

    // 8. Select Job Category
    await page.locator('.oxd-select-text').nth(2).click();
    await page.getByRole('option').nth(1).click();

    // 9. Save the job details
    await page.locator('form').filter({ hasText: 'Joined DateJob' }).getByRole('button', { name: 'Save' }).click();

    // 10. Verify successful update
    await expect(page.getByText('Successfully Updated')).toBeVisible();

    // 11. Verify Job Category is displayed
    await expect(page.locator('.oxd-select-text').nth(2)).not.toHaveText('');

    // 12. Refresh the page
    await page.reload();

    // 13. Verify Job Category persists after refresh
    await expect(page.locator('.oxd-select-text').nth(2)).not.toHaveText('');
});
