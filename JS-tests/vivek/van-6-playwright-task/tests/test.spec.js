import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:4201';
const USERNAME = 'Admin';
const PASSWORD = 'Admin@123098';

test('Update employee job details', async ({ page }) => {

    // 1. Open OrangeHRM
    await page.goto(BASE_URL);

    // 2. Login to OrangeHRM
    await page.getByPlaceholder('Username').fill(USERNAME);
    await page.getByPlaceholder('Password').fill(PASSWORD);

    // 3. Navigate to PIM
    await page.getByRole('link', { name: 'PIM' }).click();

    // 4. Navigate to Employee List
    await page.getByText('Employee List', { exact: true }).click();

    // 5. Search for employee using Employee ID
    await page.locator('input').nth(1).fill('001');
    await page.getByRole('button', { name: 'Search' }).click();

    // 6. Open the employee profile
    await page.getByRole('row', { name: '001'  }).click();

    // 7. Open the Job section
    await page.getByRole('link', { name: 'Job' }).click();

    // 8. Select Job Title
    await page.locator('.oxd-select-text').nth(0).click();
    await page.getByRole('option').nth(1).click();

    // 9. Select Employment Status
    await page.locator('.oxd-select-text').nth(1).click();
    await page.getByRole('option').nth(1).click();

    // 10. Select Job Category
    await page.locator('.oxd-select-text').nth(2).click();
    await page.getByRole('option').nth(1).click();

    // 11. Select Department
    await page.locator('.oxd-select-text').nth(3).click();
    await page.getByRole('option').nth(1).click();

    // 12. Select Location
    await page.locator('.oxd-select-text').nth(4).click();
    await page.getByRole('option').nth(1).click();

    // 13. Save the job details
    await page.locator('form').filter({ hasText: 'Joined DateJob' }).getByRole('button', { name: 'Save' }).click();

    // 14. Verify successful update
    await expect(page.getByText('Successfully Updated')).toBeVisible();

    // 15. Verify job details are displayed
    await expect(page.locator('.oxd-select-text').nth(0)).not.toHaveText('');
    await expect(page.locator('.oxd-select-text').nth(1)).not.toHaveText('');
    await expect(page.locator('.oxd-select-text').nth(2)).not.toHaveText('');
    await expect(page.locator('.oxd-select-text').nth(3)).not.toHaveText('');
    await expect(page.locator('.oxd-select-text').nth(4)).not.toHaveText('');

    // 16. Refresh the page
    await page.reload();

    // 17. Verify job details persist after refresh
    await expect(page.locator('.oxd-select-text').nth(0)).not.toHaveText('');
    await expect(page.locator('.oxd-select-text').nth(1)).not.toHaveText('');
    await expect(page.locator('.oxd-select-text').nth(2)).not.toHaveText('');
    await expect(page.locator('.oxd-select-text').nth(3)).not.toHaveText('');
    await expect(page.locator('.oxd-select-text').nth(4)).not.toHaveText('');
});
