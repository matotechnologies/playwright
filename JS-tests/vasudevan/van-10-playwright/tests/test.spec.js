import { test, expect } from '@playwright/test';

const BASE_URL = "http://localhost:4200/";

for (const browserName of ["chromium", "firefox", "webkit"]) {
    test(`ecommerce - ${browserName}`, async ({ playwright }) => {
        const browser = await playwright[browserName].launch({ headless: false });
        const page = await browser.newPage();

        await page.goto(BASE_URL);

        await page.getByPlaceholder("Search").fill("Hammer");
        await page.locator('[data-test="search-submit"]').click();

        const products = page.locator('[data-test="product-name"]');
        await expect(products.first()).toBeVisible();
        console.log("Search results:", await products.allTextContents());

        await page.goto(BASE_URL);

        const slider = page.locator('[aria-label="ngx-slider-max"]');
        await slider.click();
        await slider.press("Home");

        for (let i = 0; i < 18; i++) {
            await slider.press("ArrowRight");
        }

        const sort = page.locator('[data-test="sort"]');

        if (await sort.count() > 0) {
            await sort.selectOption("price,asc");

            const prices = await page.locator('[data-test="product-price"]').allTextContents();
            const priceValues = prices.map(price => parseFloat(price.replace(/[^\d.]/g, "")));

            expect(priceValues).toEqual([...priceValues].sort((a, b) => a - b));
            console.log("Products sorted by price");
        }

        const productNames = ["Hammer", "Bolt Cutters", "Slip Joint Pliers"];

        for (const product of productNames) {
            await page.goto(BASE_URL);

            await page.locator(`img[alt="${product}"]`).click();

            await expect(page.locator('[data-test="product-name"]')).toBeVisible();
            await expect(page.locator('[data-test="unit-price"]')).toBeVisible();

            const productName = await page.locator('[data-test="product-name"]').innerText();
            const productPrice = await page.locator('[data-test="unit-price"]').innerText();

            expect(productName).toBe(product);

            console.log("Product:", productName);
            console.log("Price:", productPrice);

            await page.getByRole("button", { name: "Add to Cart" }).click();
            await page.waitForTimeout(1000);
        }

        await page.locator('[data-test="nav-cart"]').click();

        const cartProducts = page.locator('[data-test="product-title"]');
        console.log("Cart products:", await cartProducts.allTextContents());

        const quantity = page.locator('input[data-test="product-quantity"]').first();
        await quantity.fill("3");

        await expect(quantity).toHaveValue("3");
        console.log("Updated quantity:", await quantity.inputValue());

        const buttons = page.locator('a[class="btn btn-danger"]');
        await buttons.nth(1).click();
        await buttons.nth(1).click();

        console.log("Product removed successfully");

        await page.getByRole("button", { name: "Proceed to checkout" }).click();

        await page.getByRole("tab", { name: "Continue as Guest" }).click();

        await page.get_by_placeholder("Your email").fill("customer@example.com");
        await page.get_by_placeholder("Your first name").fill("vasu");
        await page.get_by_placeholder("Your last name").fill("dev");

        await page.getByRole("button", { name: "Continue as Guest" }).click();

        await page.getByRole("button", { name: "Proceed to checkout" }).click();

        await page.locator("#country").selectOption("IN");
        await page.get_by_placeholder("Your Postcode *").fill("123456");
        await page.get_by_placeholder("e.g. 42 *").fill("33");
        await page.get_by_placeholder("Your Street *").fill("matha street");
        await page.get_by_placeholder("Your City *").fill("madurai");
        await page.get_by_placeholder("State *").fill("tamilnadu");

        await page.getByRole("button", { name: "Proceed to checkout" }).click();

        await page.locator('[data-test="payment-method"]').selectOption("Cash on Delivery");

        await page.getByRole("button", { name: "Confirm" }).click();

        const message = await page.locator('[data-test="payment-success-message"]').innerText();

        console.log(message);

        expect(message).toBe("Payment was successful");

        await browser.close();
    });
}