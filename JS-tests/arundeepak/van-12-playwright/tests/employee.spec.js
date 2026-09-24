import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BASE_URL = "http://localhost:4201/web/index.php/auth/login";
const USERNAME = 'Admin';
const PASSWORD = 'Admin@123098';

test('Create and verify employee', async ({ page }) => {
    const employeeId = 'EMP' + Math.floor(1000 + Math.random() * 9000);
    const firstName = 'Arun';
    const lastName = 'Deepak';

    await page.goto(BASE_URL);

    await page.getByPlaceholder('Username').fill(USERNAME);

    await page.getByPlaceholder('Password').fill(PASSWORD);

    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

    console.log('Login successful');

    await page.getByRole('link', { name: 'PIM' }).click();

    await page.getByRole('link', { name: 'Add Employee' }).click();

    await expect(page.getByRole('heading', { name: 'Add Employee' })).toBeVisible();

    console.log('Add Employee page opened');

    await page.getByPlaceholder('First Name').fill(firstName);

    await page.getByPlaceholder('Last Name').fill(lastName);

    const employeeIdInput = page.locator('.oxd-input-group').filter({ hasText: 'Employee Id' }).locator('input');

    await employeeIdInput.fill(employeeId);

    await page.locator('input[type="file"]').setInputFiles(path.join(__dirname, '../images/PNG1.jpg'));

    await page.getByRole('button', { name: 'Save' }).click();

    await expect(page.getByText('Successfully Saved')).toBeVisible();

    console.log('Employee created successfully');

    await page.getByText('Employee List', { exact: true }).click();

    await expect(page.getByRole('heading', { name: 'Employee Information' })).toBeVisible();

    console.log('Employee List opened');

    const employeeIdSearch = page.locator('.oxd-input-group').filter({ hasText: 'Employee Id' }).locator('input');

    await employeeIdSearch.fill(employeeId);

    await page.getByRole('button', { name: 'Search' }).click();

    await expect(page.getByText(employeeId, { exact: true })).toBeVisible();

    console.log('Employee found using Employee ID');

    const employeeRow = page.locator('.oxd-table-row').filter({ hasText: employeeId });

    await expect(employeeRow.getByText(firstName, { exact: true })).toBeVisible();

    await expect(employeeRow.getByText(lastName, { exact: true })).toBeVisible();

    console.log('Employee details verified');

    await page.getByRole('link', { name: 'PIM' }).click();

    await page.getByRole('link', { name: 'Add Employee' }).click();

    await expect(page.getByRole('heading', { name: 'Add Employee' })).toBeVisible();

    await page.getByPlaceholder('First Name').fill('Duplicate');

    await page.getByPlaceholder('Last Name').fill('Employee');

    const duplicateEmployeeId = page.locator('.oxd-input-group').filter({ hasText: 'Employee Id' }).locator('input');

    await duplicateEmployeeId.fill(employeeId);

    await page.getByRole('button', { name: 'Save' }).click();

    await expect(page.getByText('Employee Id already exists', { exact: false })).toBeVisible();

    console.log('Duplicate Employee ID rejected');

    await page.getByText('Employee List', { exact: true }).click();

    await expect(page.getByRole('heading', { name: 'Employee Information' })).toBeVisible();

    const employeeIdSearchAgain = page.locator('.oxd-input-group').filter({ hasText: 'Employee Id' }).locator('input');

    await employeeIdSearchAgain.fill(employeeId);

    await page.getByRole('button', { name: 'Search' }).click();

    const employeeRowAgain = page.locator('.oxd-table-row').filter({ hasText: employeeId });

    await expect(employeeRowAgain.getByText(employeeId, { exact: true })).toBeVisible();

    await expect(employeeRowAgain.getByText(firstName, { exact: true })).toBeVisible();

    await expect(employeeRowAgain.getByText(lastName, { exact: true })).toBeVisible();

    console.log('Employee details verified before refresh');

    await page.reload();

    const employeeIdSearchAfterRefresh = page.locator('.oxd-input-group').filter({ hasText: 'Employee Id' }).locator('input');

    await employeeIdSearchAfterRefresh.fill(employeeId);

    await page.getByRole('button', { name: 'Search' }).click();

    const employeeRowAfterRefresh = page.locator('.oxd-table-row').filter({ hasText: employeeId });

    await expect(employeeRowAfterRefresh.getByText(employeeId, { exact: true })).toBeVisible();

    await expect(employeeRowAfterRefresh.getByText(firstName, { exact: true })).toBeVisible();

    await expect(employeeRowAfterRefresh.getByText(lastName, { exact: true })).toBeVisible();

    console.log('Employee details persist after refresh');
});