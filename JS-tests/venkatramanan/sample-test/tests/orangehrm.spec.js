import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:4201';
const USERNAME = 'Admin';
const PASSWORD = 'Admin@123098'; 

test('Update employee job details', async ({ page }) => {
    
    await page.goto(`${BASE_URL}/web/index.php/auth/login`, { waitUntil: 'networkidle' });

    // 2. Complete Login (with submit button click)
    await page.locator("input[name='username']").fill(USERNAME);
    await page.locator("input[name='password']").fill(PASSWORD);
    await page.locator("button[type='submit']").click();

    // Ensure we reach the dashboard before trying to navigate menus
    await expect(page).toHaveURL(/.*\/dashboard\/index.*/, { timeout: 30000 });

    // 3. Navigate to PIM
    await page.getByRole('link', { name: 'PIM' }).click();
    await page.waitForURL('**/pim/viewEmployeeList**');

    // 4. Select the first available employee in the list (avoids hardcoding '001')
    const firstEmployeeRow = page.locator('.oxd-table-body .oxd-table-row').first();
    await expect(firstEmployeeRow).toBeVisible({ timeout: 15000 });
    await firstEmployeeRow.click();

    // 5. Open the Job tab
    const jobTab = page.getByRole('link', { name: 'Job' });
    await expect(jobTab).toBeVisible({ timeout: 10000 });
    await jobTab.click();

    // Wait for Job form to load
    await page.waitForURL('**/pim/viewJobDetails/empNumber/**');

    // 6. Select first Job Title dropdown
    const jobTitleDropdown = page.locator('.oxd-select-text').first();
    await jobTitleDropdown.click();
    const dropdownOption = page.locator('.oxd-select-dropdown .oxd-select-option').nth(1);
    await dropdownOption.waitFor({ state: 'visible' });
    await dropdownOption.click();

    // 7. Save the job details
    const saveButton = page.locator('form').filter({ hasText: 'Joined Date' }).getByRole('button', { name: 'Save' });
    if (await saveButton.isVisible()) {
        await saveButton.click();
    } else {
        // Fallback for screens where the section has a general Save button
        await page.locator("button[type='submit']").first().click();
    }

    // 8. Verify toast notification appears
    const successToast = page.locator('.oxd-toast--success');
    await expect(successToast).toBeVisible({ timeout: 10000 });

    // 9. Reload and verify dropdown is not empty
    await page.reload({ waitUntil: 'networkidle' });
    await expect(page.locator('.oxd-select-text').first()).not.toHaveText('-- Select --');
});
