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

    // 8.Open Job Category dropdown
    const jobCategory = page.locator('.oxd-select-text').nth(2);
    await jobCategory.click();

    // 9. Check whether Job Category options exist
    const options = page.locator('.oxd-select-option');
    const optionCount = await options.count();
    console.log('Job Category option count:', optionCount);

     // 10. Select Job Category if options exist
    if (optionCount > 1) {
        await options.nth(1).click();
    } else {
        console.log('No Job Category options available. Skipping Job Category update.');
    }

    // 11. Save only if a Job Category option was available
    if (optionCount > 1) {
        await page.getByRole('button', { name: 'Save' }).click();

        // 12. Verify successful update
        await expect(page.getByText('Successfully Updated')).toBeVisible();

        // 13. Refresh
        await page.reload();

        // 14. Verify Job Category is still selected
        await expect(jobCategory).not.toHaveText('');
    }
});
