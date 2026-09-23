import re
import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:4200/"

@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_ecommerce(browser_name):

    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=False)
        page = browser.new_page()

        page.goto(BASE_URL)

        page.get_by_placeholder("Search").fill("Hammer")
        page.locator('[data-test="search-submit"]').click()

        products = page.locator('[data-test="product-name"]')
        expect(products.first).to_be_visible()
        print("Search results:", products.all_text_contents())

        page.goto(BASE_URL)

        slider = page.locator('[aria-label="ngx-slider-max"]')
        slider.click()
        slider.press("Home")

        for _ in range(18):
            slider.press("ArrowRight")

        sort = page.locator('[data-test="sort"]')

        if sort.count() > 0:
            sort.select_option("price,asc")

            prices = page.locator('[data-test="product-price"]').all_text_contents()

            price_values = [float(re.sub(r"[^\d.]", "", price))for price in prices]

            assert price_values == sorted(price_values)
            print("Products sorted by price")

        product_names = ["Hammer", "Bolt Cutters", "Slip Joint Pliers"]

        for product in product_names:
            page.goto(BASE_URL)

            page.locator(f'img[alt="{product}"]').click()

            expect(page.locator('[data-test="product-name"]')).to_be_visible()
            expect(page.locator('[data-test="unit-price"]')).to_be_visible()

            product_name = page.locator('[data-test="product-name"]').inner_text()
            product_price = page.locator('[data-test="unit-price"]').inner_text()

            assert product_name == product

            print("Product:", product_name)
            print("Price:", product_price)

            page.get_by_role("button", name="Add to Cart").click()
            expect(page.get_by_text("Product added to Shopping cart")).to_be_visible()

        page.locator('[data-test="nav-cart"]').click()

        cart_products = page.locator('[data-test="product-title"]')
        print("Cart products:", cart_products.all_text_contents())

        quantity = page.locator('input[data-test="product-quantity"]').first
        quantity.fill("3")

        assert quantity.input_value() == "3"
        print("Updated quantity:", quantity.input_value())

        buttons = page.locator('a[class="btn btn-danger"]')
        buttons.nth(1).click()
        

        print("Product removed successfully")

        page.get_by_role("button", name="Proceed to checkout").click()

        page.get_by_role("tab", name="Continue as Guest").click()

        page.locator("#guest-email").fill("customer@example.com")
        page.get_by_placeholder("Your first name").fill("vasu")
        page.get_by_placeholder("Your last name").fill("dev")

        page.get_by_role("button", name="Continue as Guest").click()

        page.get_by_role("button", name="Proceed to checkout").click()

        page.locator("#country").select_option("IN")
        page.get_by_placeholder("Your Postcode *").fill("123456")
        page.get_by_placeholder("e.g. 42 *").fill("33")
        page.get_by_placeholder("Your Street *").fill("matha street")
        page.get_by_placeholder("Your City *").fill("madurai")
        page.get_by_placeholder("State *").fill("tamilnadu")

        page.get_by_role("button", name="Proceed to checkout").click()

        page.locator('[data-test="payment-method"]').select_option("Cash on Delivery")

        page.get_by_role("button", name="Confirm").click()

        message = page.locator('[data-test="payment-success-message"]').inner_text()

        print(message)

        assert message == "Payment was successful"

        browser.close()