import { test, expect } from '@playwright/test';


const BASE_URL = 'http://localhost:4200';
const PASSWORD = 'ArunDeepak*123';


async function registerUser(page) {

    const email = `arundeepak${Math.floor(10000 + Math.random() * 90000)}@example.com`;

    await page.goto(`${BASE_URL}/auth/register`);

    await page.getByPlaceholder('First name *').fill('Arun');

    await page.getByPlaceholder('Your last name *').fill('Deepak');

    await page.getByPlaceholder('YYYY-MM-DD').fill('1999-01-01');

    await page.locator('#country').selectOption('IN');

    await page.getByPlaceholder('Your Postcode *').fill('630606');

    await page.getByPlaceholder('e.g. 42 *').fill('32-E');

    await page.getByPlaceholder('Your Street *').fill('Main Street');

    await page.getByPlaceholder('Your City *').fill('Manamadurai');

    await page.getByPlaceholder('Your State *').fill('Tamil Nadu');

    await page.locator("[data-test='phone']").fill('9876543210');

    await page.getByPlaceholder('Your email *').fill(email);

    await page.getByPlaceholder('Your password').fill(PASSWORD);

    await page.getByRole('button', { name: 'Register' }).click();

    console.log('Registration URL:', page.url());

    console.log('Registration page:', await page.locator('body').innerText());

    await expect(page).toHaveURL(`${BASE_URL}/auth/login`);

    console.log('REGISTER EMAIL:', email);

    return email;
}


async function login(page, email) {

    await page.goto(`${BASE_URL}/auth/login`);

    await page.getByPlaceholder('Your email').fill(email);

    await page.getByPlaceholder('Your password').fill(PASSWORD);

    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page).toHaveURL(`${BASE_URL}/account`);
}


test('application accessible', async ({ page }) => {

    await page.goto(BASE_URL);

    await expect(page.locator('#Layer_1')).toBeVisible();
});


test('session persistence', async ({ page }) => {

    const email = await registerUser(page);

    await login(page, email);

    await expect(page).toHaveURL(`${BASE_URL}/account`);

    await page.reload();

    await expect(page).toHaveURL(`${BASE_URL}/account`);
});


test('new browser context', async ({ page, browser }) => {

    const email = await registerUser(page);

    await login(page, email);

    await expect(page).toHaveURL(`${BASE_URL}/account`);

    const context = await browser.newContext();

    const newPage = await context.newPage();

    await newPage.goto(`${BASE_URL}/account`);

    await expect(newPage).toHaveURL(`${BASE_URL}/auth/login`);

    await context.close();
});


test('logout', async ({ page }) => {

    const email = await registerUser(page);

    await login(page, email);

    await expect(page).toHaveURL(`${BASE_URL}/account`);

    await page.locator("[data-test='nav-menu']").click();

    await page.locator("[data-test='nav-sign-out']").click();

    await expect(page).toHaveURL(`${BASE_URL}/auth/login`);
});


test('invalid login', async ({ page }) => {

    await page.goto(`${BASE_URL}/auth/login`);

    await page.getByPlaceholder('Your email').fill('invalid@example.com');

    await page.getByPlaceholder('Your password').fill('WrongPassword*123');

    await page.getByRole('button', { name: 'Login' }).click();


    console.log('Login URL:', page.url());

    console.log('Login page:', await page.locator('body').innerText());

    await expect(page).toHaveURL(`${BASE_URL}/auth/login`);

    await expect(page.getByText('Invalid email or password')).toBeVisible();
});


test('required fields', async ({ page }) => {

    await page.goto(`${BASE_URL}/auth/register`);

    await expect(page.getByPlaceholder('First name *')).toHaveAttribute('aria-required', 'true');

    await expect(page.getByPlaceholder('Your last name *')).toHaveAttribute('aria-required', 'true');

    await expect(page.getByPlaceholder('Your Postcode *')).toHaveAttribute('aria-required', 'true');

    await expect(page.getByPlaceholder('Your email *')).toHaveAttribute('aria-required', 'true');
});


test('authentication storage', async ({ page }) => {

    const email = await registerUser(page);

    await login(page, email);

    await expect(page).toHaveURL(`${BASE_URL}/account`);

    const cookies = await page.context().cookies();

    const localStorage = await page.evaluate(() => {
        return Object.entries(localStorage);
    });

    const sessionStorage = await page.evaluate(() => {
        return Object.entries(sessionStorage);
    });

    console.log('Cookies:', cookies);
    console.log('Local Storage:', localStorage);
    console.log('Session Storage:', sessionStorage);

    expect(
        cookies.length > 0 ||
        localStorage.length > 0 ||
        sessionStorage.length > 0
    ).toBeTruthy();
});
