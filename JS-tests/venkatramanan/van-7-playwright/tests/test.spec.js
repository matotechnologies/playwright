const { test, expect } = require('@playwright/test');

test.describe('Toolshop End-to-End Dynamic Automation', () => {
  
  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status !== testInfo.expectedStatus) {
      const screenshotPath = `failure-${testInfo.title.replace(/\s+/g, '_')}.png`;
      await page.screenshot({ path: screenshotPath, fullPage: true });
    }
  });

  test.beforeEach(async ({ page }) => {
 
    await page.goto('http://localhost:4200');
    await expect(page).toHaveTitle(/Practice Software Testing/i);
    await expect(page.locator('.card-title').first()).toBeVisible();
  });

  test('Dynamic Search: search and validate without hardcoded strings', async ({ page }) => {
    
    const firstProductTitle = await page.locator('.card-title').first().innerText();
    const dynamicSearchKeyword = firstProductTitle.trim().split(' ')[0]; 

    const searchInput = page.locator('[data-test="search-query"]');
    await searchInput.fill(dynamicSearchKeyword);
    await page.getByRole('button', { name: 'Search' }).click();

    const cardTitles = page.locator('.card-title');
    await expect(cardTitles.first()).toBeVisible();

    const titles = await cardTitles.allInnerTexts();
    expect(titles.length).toBeGreaterThan(0);
    for (const title of titles) {
      expect(title.toLowerCase()).toContain(dynamicSearchKeyword.toLowerCase());
    }
  });

  test('Apply Sorting and validate ascending order', async ({ page }) => {
    
    const sortDropdown = page.locator('[data-test="sort"]');
    await sortDropdown.selectOption('price,asc');

    await expect.poll(async () => {
      const priceTexts = await page.locator('[data-test="product-price"]').allInnerTexts();
      const prices = priceTexts.map(p => parseFloat(p.replace(/[^0-9.]/g, '')));
      if (prices.length === 0) return false;
      for (let i = 0; i < prices.length - 1; i++) {
        if (prices[i] > prices[i + 1]) return false;
      }
      return true;
    },).toBe(true);
  });

  test('Dynamic Pagination handling', async ({ page }) => {
    
    const pagination = page.locator('ul.pagination');
    if (await pagination.isVisible()) {
      const initialFirstProduct = await page.locator('.card-title').first().innerText();
      const pageTwoButton = pagination.locator('.page-item', { hasText: '2' });

      if (await pageTwoButton.isVisible()) {
        await pageTwoButton.click();
        
        await expect(page.locator('.card-title').first()).not.toHaveText(initialFirstProduct);
      }
    }
  });

  test('Dynamic selection and product details validation', async ({ page }) => {
    const targetCard = page.locator('a.card').first();
    const expectedTitle = (await targetCard.locator('.card-title').innerText()).trim();
    const rawExpectedPrice = (await targetCard.locator('[data-test="product-price"]').innerText()).trim();

    
    const numericPrice = rawExpectedPrice.replace(/[^0-9.]/g, '');

    await targetCard.click();
    await page.waitForURL(/.*\/product\/.*/);

    const detailsTitle = page.locator('[data-test="product-name"]');
    const detailsPrice = page.locator('[data-test="unit-price"]');

    await expect(detailsTitle).toBeVisible();
    await expect(detailsTitle).toHaveText(expectedTitle);
    await expect(detailsPrice).toContainText(numericPrice);
  });
});