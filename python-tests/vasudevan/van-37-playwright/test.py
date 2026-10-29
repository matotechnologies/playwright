from playwright.sync_api import expect, sync_playwright


def price_conversion(value):
    return f"{round(value, 2):.2f}"
BaseURL = "https://practicesoftwaretesting.com/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(BaseURL)
    page.wait_for_load_state()

    cards = page.locator(".card")
    expect(cards.first).to_be_visible()

    available_product_name = None
    for i in range(cards.count()):
        card = cards.nth(i)
        if card.locator('[data-test="out-of-stock"]').count() > 0:
            continue
        available_product_name = card.locator("h5").inner_text().strip()
        break

    assert available_product_name is not None, "No available product found"
    print("First available product:", available_product_name)


    cards.filter(has_text=available_product_name).first.click()

    product_name_locator = page.locator('h1[data-test="product-name"]')
    expect(product_name_locator).to_be_visible()
    product_name = product_name_locator.text_content().strip()

    price_locator = page.locator('span[aria-label="unit-price"]')
    expect(price_locator).to_be_visible()
    product_price = float(price_locator.text_content().strip())
    print("Selected:", product_name, product_price)

    page.get_by_role('button', name='Add to Cart').click()


    page.locator('[data-test="nav-cart"]').click()

    cart_titles = page.locator('span[data-test="product-title"]')
    expect(cart_titles).to_have_count(1)
    expect(cart_titles.first).to_have_text(product_name)

    cart_price = page.locator('span[data-test="product-price"]')
    assert float(cart_price.first.text_content().strip()[1:]) == product_price

    expect(page.locator('input[data-test="product-quantity"]').first).to_have_value("1")
    print("Cart shows the correct product, price and quantity")

   
    quantities = page.locator('input[data-test="product-quantity"]')
    quantities.first.fill("2")
    quantities.first.press("Tab")
    expect(quantities.first).to_have_value("2")
    print("Quantity updated to 2")

   
    cart_total = page.locator('[data-test="cart-total"]')
    expect(cart_total).to_contain_text(price_conversion(product_price * 2))
    print("Subtotal correct:", price_conversion(product_price * 2))

  
    page.goto(BaseURL)
    page.wait_for_load_state("networkidle")

    cards = page.locator(".card")
    expect(cards.first).to_be_visible()

    cards = page.locator(".card")
    expect(cards.first).to_be_visible()

    second_product_name = None

    for i in range(cards.count()):
        card = cards.nth(i)
        if card.locator('[data-test="out-of-stock"]').count() > 0:
            continue
        candidate = card.locator("h5").inner_text().strip()
        if candidate == product_name:
            continue

        second_product_name = candidate
        card.locator("h5").click()
        break

    assert second_product_name is not None, "No second available product found"
    page.wait_for_url("**/product/**")

    product_name_b_locator = page.locator('h1[data-test="product-name"]')
    expect(product_name_b_locator).to_be_visible()
    product_name_b = product_name_b_locator.text_content().strip()

    price_b_locator = page.locator('span[aria-label="unit-price"]')
    expect(price_b_locator).to_be_visible()
    price_b = float(price_b_locator.text_content().strip())
    print("Second product:", product_name_b, price_b)

    page.get_by_role('button', name='Add to Cart').click()
    expect(page.get_by_text("Product added to shopping cart")).to_be_visible()
    
    page.locator('[data-test="nav-cart"]').click()
    expect(cart_titles).to_have_count(2)
    expect(cart_titles.nth(0)).to_have_text(product_name)
    expect(cart_titles.nth(1)).to_have_text(product_name_b)
    expect(quantities.nth(0)).to_have_value("2")
    expect(quantities.nth(1)).to_have_value("1")

    expected_both = (product_price * 2) + (price_b * 1)
    expect(cart_total).to_contain_text(price_conversion(expected_both))
    print("Both products present, total:", price_conversion(expected_both))

    page.locator('a[class="btn btn-danger"]').nth(1).click()
    expect(cart_titles).to_have_count(1)
    expect(cart_titles.first).to_have_text(product_name)
    expect(quantities.first).to_have_value("2")
    print("Remaining product:", product_name)

    expect(cart_total).to_contain_text(price_conversion(product_price * 2))
    print("Subtotal recalculated:", price_conversion(product_price * 2))

   
    page.reload()
    page.wait_for_load_state()

    expect(cart_titles).to_have_count(1)
    expect(cart_titles.first).to_have_text(product_name)
    expect(quantities.first).to_have_value("2")
    expect(cart_total).to_contain_text(price_conversion(product_price * 2))
    print("Cart state preserved after reload")

    browser.close()