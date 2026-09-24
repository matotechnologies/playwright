import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:4200"


def wait_for_products_loaded(page: Page):
    
    first_title = page.locator(".card-title").first
    expect(first_title).to_be_visible()
    expect(first_title).not_to_have_text("")


def test_search_product(page: Page):
    page.goto(BASE_URL)
    wait_for_products_loaded(page)

    with page.expect_response(lambda r: "/products" in r.url and r.status == 200):
        page.fill('[data-test="search-query"]', "pliers")
        search_btn = page.locator('[data-test="search-submit"]')
        if search_btn.is_visible():
            search_btn.click()
        else:
            page.press('[data-test="search-query"]', "Enter")

    wait_for_products_loaded(page)

    cards = page.locator(".card-title")
    expect(cards.first).to_be_visible()

    products = [p.strip().lower() for p in cards.all_inner_texts() if p.strip()]
    assert len(products) > 0, "No products found for 'pliers' search"
    for name in products:
        assert "pliers" in name, f"Expected 'pliers' in product name, got '{name}'"


def test_apply_filter(page: Page):
    page.goto(BASE_URL)
    wait_for_products_loaded(page)

    initial_products = [p.strip() for p in page.locator(".card-title").all_inner_texts() if p.strip()]

    checkbox = page.locator('input[type="checkbox"]').first
    expect(checkbox).to_be_visible()

    with page.expect_response(lambda r: "/products" in r.url and r.status == 200):
        checkbox.check()

    wait_for_products_loaded(page)

    filtered_products = [p.strip() for p in page.locator(".card-title").all_inner_texts() if p.strip()]
    assert len(filtered_products) > 0, "Filter returned zero products"
    assert filtered_products != initial_products, "Filter selection did not alter the displayed product list"


def test_apply_sorting(page: Page):
    page.goto(BASE_URL)
    wait_for_products_loaded(page)

    
    initial_first_title = page.locator(".card-title").first.inner_text().strip()

    with page.expect_response(lambda r: "/products" in r.url and r.status == 200):
        page.select_option('[data-test="sort"]', value="name,asc")


    first_card = page.locator(".card-title").first
    expect(first_card).not_to_have_text(initial_first_title)

  
    product_names = [p.strip() for p in page.locator(".card-title").all_inner_texts() if p.strip()]
    assert len(product_names) > 0, "No products displayed after sorting"
    assert product_names == sorted(product_names, key=str.casefold), "Products are not sorted alphabetically (A-Z)"
