import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:4200';

test('Toolshop cart checkout', async ({ page }) => {

    // 1. Open Toolshop locally
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle('Practice Software Testing - Toolshop - v5.0');
    console.log('Toolshop opened successfully');

    // 2. Select multiple available products dynamically
    const productCards = page.locator("a[href^='/product/']");
    await expect(productCards.first()).toBeVisible();

    const productCount = await productCards.count();
    console.log('Products found:', productCount);

    const selectedProducts = [];

    for (let i = 0; i < productCount; i++) {
        const product = productCards.nth(i);
        const productName = (await product.innerText()).trim();

        if (productName.includes('Out of stock')) {
            console.log('Skipping unavailable product');
            continue;
        }

        const productUrl = await product.getAttribute('href');

        selectedProducts.push({
            name: productName.split('\n')[0],
            url: productUrl
        });

        console.log(`Selected product: ${productName.split('\n')[0]}`);

        if (selectedProducts.length === 2) {
            break;
        }
    }

    expect(selectedProducts.length).toBe(2);

    // 3. Add products to cart
    const selectedProductData = [];

    for (const productInfo of selectedProducts) {
        await page.goto(BASE_URL);

        const productCards = page.locator("a[href^='/product/']");
        await expect(productCards.first()).toBeVisible();

        const productLink = page.locator(`a[href='${productInfo.url}']`);
        await expect(productLink).toBeVisible();

        console.log(`Opening product: ${productInfo.name}`);

        await productLink.click();

        const productNameLocator = page.locator('h1');
        await expect(productNameLocator).toBeVisible();

        const productName = (await productNameLocator.innerText()).trim();

        const priceText = await page.locator('text=/\\$\\d+\\.\\d+/').first().innerText();
        const price = parseFloat(priceText.replace('$', '').trim());

        console.log(`Product: ${productName} | Price: $${price.toFixed(2)}`);

        const addToCartButton = page.getByRole('button', { name: 'Add to cart' });
        await expect(addToCartButton).toBeVisible();

        await addToCartButton.click();

        const cartLink = page.locator("a[href='/checkout']");
        const expectedCartCount = selectedProductData.length + 1;

        await expect(cartLink).toContainText(String(expectedCartCount));

        console.log(`Added to cart: ${productName} | Cart count: ${expectedCartCount}`);

        selectedProductData.push({
            name: productName,
            price: price,
            quantity: 1
        });
    }

    // 4. Open cart
    const cartLink = page.getByRole('link', { name: 'Cart' });

    await expect(cartLink).toBeVisible();
    await cartLink.click();

    await expect(page.locator('table')).toBeVisible();

    console.log('Cart opened');

    // 5. Validate cart contents
    const cartTable = page.locator('table');

    for (const product of selectedProductData) {
        const productRow = cartTable.locator('tr').filter({ hasText: product.name }).first();

        await expect(productRow).toBeVisible();

        console.log(`Verified in cart: ${product.name}`);
    }

    console.log('All selected products are present in the cart');

    // 6. Validate individual product prices
    let expectedSubtotal = 0;

    const productRows = cartTable.locator('tbody').first().locator('tr');
    const rowCount = await productRows.count();

    console.log(`Product rows found in cart: ${rowCount}`);

    for (const product of selectedProductData) {
        const productName = product.name;
        const expectedPrice = product.price;
        const quantity = product.quantity;

        let matchingRow = null;

        for (let i = 0; i < rowCount; i++) {
            const row = productRows.nth(i);
            const firstCell = row.locator('td').first();
            const cellText = (await firstCell.innerText()).trim();

            if (cellText === productName) {
                matchingRow = row;
                break;
            }
        }

        expect(matchingRow).not.toBeNull();
        await expect(matchingRow).toBeVisible();

        const rowText = await matchingRow.innerText();

        console.log(`Cart details for ${productName}: ${rowText.trim()}`);

        const priceMatches = [...rowText.matchAll(/\$(\d+\.\d+)/g)].map(match => match[1]);

        expect(priceMatches.length).toBeGreaterThanOrEqual(2);

        const cartPrice = parseFloat(priceMatches[0]);
        const rowTotal = parseFloat(priceMatches[priceMatches.length - 1]);

        expect(cartPrice).toBe(expectedPrice);

        console.log(`Price verified: ${productName} = $${cartPrice.toFixed(2)}`);

        const expectedRowTotal = expectedPrice * quantity;

        expect(rowTotal).toBe(expectedRowTotal);

        console.log(`Product total verified: ${productName} = $${rowTotal.toFixed(2)}`);

        expectedSubtotal += expectedRowTotal;
    }

    console.log(`Expected subtotal: $${expectedSubtotal.toFixed(2)}`);

    // 7. Modify product quantity
    console.log('Modifying product quantities...');

    const firstProduct = selectedProductData[0];
    const productName = firstProduct.name;

    const quantityInput = page.getByRole('spinbutton', { name: `Quantity for ${productName}` });

    await expect(quantityInput).toBeVisible();

    await quantityInput.fill('2');
    await quantityInput.press('Enter');

    await expect(quantityInput).toHaveValue('2');

    firstProduct.quantity = 2;

    let updatedExpectedSubtotal = 0;

    for (const product of selectedProductData) {
        updatedExpectedSubtotal += product.price * product.quantity;
    }

    console.log(`Updated expected subtotal: $${updatedExpectedSubtotal.toFixed(2)}`);

    // 8. Recalculate expected subtotal
    expectedSubtotal = 0;

    for (const product of selectedProductData) {
        const productName = product.name;
        const quantity = product.quantity;
        const price = product.price;

        expectedSubtotal += price * quantity;
    }

    console.log(`Expected subtotal after quantity update: $${expectedSubtotal.toFixed(2)}`);

    // 9. Compare expected subtotal with application
    const cartRows = cartTable.locator('tr');

    let totalRow = null;

    for (let i = 0; i < await cartRows.count(); i++) {
        const row = cartRows.nth(i);
        const rowText = (await row.innerText()).trim();

        if (rowText.startsWith('Total')) {
            totalRow = row;
            break;
        }
    }

    expect(totalRow).not.toBeNull();
    await expect(totalRow).toBeVisible();

    await expect(totalRow).toContainText(`$${updatedExpectedSubtotal.toFixed(2)}`);

    const totalText = await totalRow.innerText();

    const totalMatches = [...totalText.matchAll(/\$(\d+\.\d+)/g)].map(match => match[1]);

    expect(totalMatches.length).toBeGreaterThanOrEqual(1);

    const applicationSubtotal = parseFloat(totalMatches[totalMatches.length - 1]);

    console.log(`Application subtotal: $${applicationSubtotal.toFixed(2)}`);

    expect(applicationSubtotal).toBeCloseTo(updatedExpectedSubtotal, 2);

    console.log('Subtotal verified successfully');

    // 10. Remove a product
    console.log('Removing a product...');

    const productToRemove = selectedProductData[0];
    const productNameToRemove = productToRemove.name;

    const productRowsForRemoval = cartTable.locator('tbody').first().locator('tr');

    let matchingRowForRemoval = null;

    for (let i = 0; i < await productRowsForRemoval.count(); i++) {
        const row = productRowsForRemoval.nth(i);
        const firstCell = row.locator('td').first();
        const cellText = (await firstCell.innerText()).trim();

        if (cellText === productNameToRemove) {
            matchingRowForRemoval = row;
            break;
        }
    }

    expect(matchingRowForRemoval).not.toBeNull();
    await expect(matchingRowForRemoval).toBeVisible();

    console.log(`Product selected for removal: ${productNameToRemove}`);

    const removeLink = matchingRowForRemoval.locator('a.btn.btn-danger');

    await expect(removeLink).toBeVisible();

    await removeLink.click();

    await expect(
        cartTable.locator('tbody').first().locator('tr').filter({ hasText: productNameToRemove })
    ).toHaveCount(0);

    console.log(`Product removed successfully: ${productNameToRemove}`);

    // 11. Calculate expected subtotal after removal
    let expectedUpdatedSubtotal = 0;

    for (const product of selectedProductData) {
        if (product.name === productNameToRemove) {
            continue;
        }

        expectedUpdatedSubtotal += product.price * product.quantity;
    }

    console.log(
        `Expected subtotal after removing ${productNameToRemove}: $${expectedUpdatedSubtotal.toFixed(2)}`
    );

    // 12. Validate updated application total
    const updatedCartRows = cartTable.locator('tr');

    let updatedTotalRow = null;

    for (let i = 0; i < await updatedCartRows.count(); i++) {
        const row = updatedCartRows.nth(i);
        const rowText = (await row.innerText()).trim();

        if (rowText.startsWith('Total')) {
            updatedTotalRow = row;
            break;
        }
    }

    expect(updatedTotalRow).not.toBeNull();
    await expect(updatedTotalRow).toBeVisible();

    await expect(updatedTotalRow).toContainText(
        `$${expectedUpdatedSubtotal.toFixed(2)}`
    );

    const updatedTotalText = await updatedTotalRow.innerText();

    const updatedTotalMatches = [
        ...updatedTotalText.matchAll(/\$(\d+\.\d+)/g)
    ].map(match => match[1]);

    expect(updatedTotalMatches.length).toBeGreaterThanOrEqual(1);

    const updatedApplicationTotal = parseFloat(
        updatedTotalMatches[updatedTotalMatches.length - 1]
    );

    console.log(`Expected updated total: $${expectedUpdatedSubtotal.toFixed(2)}`);
    console.log(`Application updated total: $${updatedApplicationTotal.toFixed(2)}`);

    expect(updatedApplicationTotal).toBeCloseTo(expectedUpdatedSubtotal, 2);

    console.log('Updated subtotal verified successfully');

    // 13. Reload page and verify cart state
    console.log('Reloading cart page...');

    await page.reload();
    await page.waitForLoadState('domcontentloaded');

    await expect(page.locator('table')).toBeVisible();

    const reloadedCartTable = page.locator('table');

    const productRowsAfterReload = reloadedCartTable.locator('tbody').first().locator('tr');

    let removedProductFound = false;

    for (let i = 0; i < await productRowsAfterReload.count(); i++) {
        const row = productRowsAfterReload.nth(i);
        const firstCell = row.locator('td').first();
        const cellText = (await firstCell.innerText()).trim();

        if (cellText === productNameToRemove) {
            removedProductFound = true;
            break;
        }
    }

    expect(removedProductFound).toBe(false);

    console.log(
        `Verified removed product is absent after reload: ${productNameToRemove}`
    );

    const remainingProducts = selectedProductData.filter(
        product => product.name !== productNameToRemove
    );

    for (const product of remainingProducts) {
        const productNameAfterReload = product.name;
        let productFound = false;

        for (let i = 0; i < await productRowsAfterReload.count(); i++) {
            const row = productRowsAfterReload.nth(i);
            const firstCell = row.locator('td').first();
            const cellText = (await firstCell.innerText()).trim();

            if (cellText === productNameAfterReload) {
                productFound = true;
                break;
            }
        }

        expect(productFound).toBe(true);

        console.log(
            `Verified product after reload: ${productNameAfterReload}`
        );
    }

    console.log('Cart state verified successfully after reload');

    // 14. Continue to checkout
    await page.getByRole('button', { name: 'Proceed to checkout' }).click();

    console.log('Checkout page opened');

    // 15. Validate mandatory checkout fields
    console.log('Validating mandatory checkout fields...');

    const checkoutForms = page.locator('form');

    await expect(checkoutForms).toHaveCount(4);

    console.log('Checkout forms verified: 4');

    const visibleForm = page.locator('form:visible').first();

    await expect(visibleForm).toBeVisible();

    console.log('Visible checkout form found');

    const visibleInputs = visibleForm.locator('input:visible');
    const inputCount = await visibleInputs.count();

    console.log(`Visible input fields found: ${inputCount}`);

    expect(inputCount).toBeGreaterThan(0);


    const emailField = visibleForm.getByRole('textbox', { name: 'Email address *' });
    const passwordField = visibleForm.getByRole('textbox', { name: 'Password *' });

    await expect(emailField).toBeVisible();
    await expect(passwordField).toBeVisible();

    console.log('Mandatory email field is visible');
    console.log('Mandatory password field is visible');

    await expect(emailField).toHaveValue('');
    await expect(passwordField).toHaveValue('');

    console.log('Mandatory checkout fields validated successfully');

    // 16. Complete checkout fields
    console.log('Completing checkout as guest...');

    const guestTab = page.getByRole('tab', { name: 'Continue as Guest' });

    await expect(guestTab).toBeVisible();

    await guestTab.click();

    console.log('Continue as Guest selected');

    const guestForm = page.locator('form:visible').first();

    await expect(guestForm).toBeVisible();

    console.log('Guest checkout form opened');

    const guestEmail = guestForm.getByRole('textbox', { name: 'Email address *' });
    const guestFirstName = guestForm.getByRole('textbox', { name: 'First name *' });
    const guestLastName = guestForm.getByRole('textbox', { name: 'Last name *' });

    await expect(guestEmail).toBeVisible();
    await expect(guestFirstName).toBeVisible();
    await expect(guestLastName).toBeVisible();

    await guestEmail.fill('vivek@example.com');
    await guestFirstName.fill('Vivek');
    await guestLastName.fill('NP');

    await expect(guestEmail).toHaveValue('vivek@example.com');
    await expect(guestFirstName).toHaveValue('Vivek');
    await expect(guestLastName).toHaveValue('NP');

    console.log('Guest email entered');
    console.log('Guest first name entered');
    console.log('Guest last name entered');

    const continueGuestButton = guestForm.getByRole(
        'button',
        { name: 'Continue as Guest' }
    );

    await expect(continueGuestButton).toBeVisible();

    await continueGuestButton.click();

    console.log('Guest checkout details submitted');

    const proceedGuestButton = page.locator("[data-test='proceed-2-guest']");

    await expect(proceedGuestButton).toBeVisible();
    await expect(proceedGuestButton).toBeEnabled();

    await proceedGuestButton.click();

    console.log('Proceed to checkout clicked');
    console.log('Billing address page opened');

    const billingForm = page.locator('form:visible').first();

    await expect(billingForm).toBeVisible();

    console.log('Billing address form opened');

    const country = billingForm.getByRole('combobox', { name: 'Country' });

    await expect(country).toBeVisible();
    await expect(country).toBeEnabled();

    console.log('Country field is visible');

    await country.selectOption({ label: 'India' });

    console.log('Country selected: India');

    const postalCode = billingForm.getByPlaceholder('Your Postcode *');
    const houseNumber = billingForm.getByPlaceholder('e.g. 42 *');
    const street = billingForm.getByPlaceholder('Your Street *');
    const city = billingForm.getByPlaceholder('Your City *');
    const state = billingForm.getByPlaceholder('State *');

    await expect(postalCode).toBeVisible();
    await expect(houseNumber).toBeVisible();
    await expect(street).toBeVisible();
    await expect(city).toBeVisible();
    await expect(state).toBeVisible();

    await postalCode.fill('570001');
    await houseNumber.fill('42');
    await street.fill('Sayyaji Rao Road');
    await city.fill('Mysore');
    await state.fill('Karnataka');

    await expect(postalCode).toHaveValue('570001');
    await expect(houseNumber).toHaveValue('42');
    await expect(street).toHaveValue('Sayyaji Rao Road');
    await expect(city).toHaveValue('Mysore');
    await expect(state).toHaveValue('Karnataka');

    const proceedButton = page.locator("[data-test='proceed-3']");

    await expect(proceedButton).toBeVisible();
    await expect(proceedButton).toBeEnabled();

    await proceedButton.click();

    console.log('Proceed to payment clicked');
    console.log('Payment page opened');

    // 17. Select payment method
    console.log('Selecting payment method...');

    const paymentMethod = page.locator("[data-test='payment-method']");

    await expect(paymentMethod).toBeVisible();
    await expect(paymentMethod).toBeEnabled();

    await paymentMethod.selectOption({ label: 'Cash on Delivery' });

    await expect(paymentMethod).toHaveValue('cash-on-delivery');

    console.log('Payment method selected: Cash on Delivery');

    // 18. Complete checkout
    await page.getByRole('button', { name: 'Confirm' }).click();

    // 19. Verify payment success
    console.log('Verifying payment success...');

    const paymentSuccessMessage = page.locator(
        "[data-test='payment-success-message']"
    );

    await expect(paymentSuccessMessage).toBeVisible();

    await expect(paymentSuccessMessage).toHaveText(
        'Payment was successful'
    );

    console.log('Payment successful message verified');
});

