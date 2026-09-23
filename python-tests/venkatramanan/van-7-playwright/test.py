import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:4200"
TIMEOUT = 30000


def wait_for_products_loaded(page: Page):
    
    first_title = page.locator(".card-title").first
    expect(first_title).to_be_visible(timeout=TIMEOUT)
    expect(first_title).not_to_have_text("", timeout=TIMEOUT)


def test_search_product(page: Page):
    page.goto(BASE_URL)
    wait_for_products_loaded(page)

    with page.expect_response(
        lambda r: "/products" in r.url and r.status == 200, 
        timeout=TIMEOUT
    ):
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
    expect(checkbox).to_be_visible(timeout=TIMEOUT)

    with page.expect_response(
        lambda r: "/products" in r.url and r.status == 200, 
        timeout=TIMEOUT
    ):
        checkbox.check()

    wait_for_products_loaded(page)

    filtered_products = [p.strip() for p in page.locator(".card-title").all_inner_texts() if p.strip()]
    assert len(filtered_products) > 0, "Filter returned zero products"
    assert filtered_products != initial_products, "Filter selection did not alter the displayed product list"


def test_apply_sorting(page: Page):
    page.goto(BASE_URL)
    wait_for_products_loaded(page)

    page.select_option('[data-test="sort"]', value="name,asc")

    page.wait_for_function(
        """() => {
            const titles = Array.from(document.querySelectorAll('.card-title'))
                .map(el => el.textContent.trim().toLowerCase())
                .filter(t => t.length > 0);
            if (titles.length === 0) return false;
            for (let i = 0; i < titles.length - 1; i++) {
                if (titles[i].localeCompare(titles[i + 1]) > 0) return false;
            }
            return true;
        }""",
        timeout=TIMEOUT
    )

    products = [p.strip() for p in page.locator(".card-title").all_inner_texts() if p.strip()]
    assert len(products) > 0, "No products visible after sorting"
    assert products == sorted(products, key=str.lower), "Products are not sorted alphabetically (A-Z)"


def test_pagination(page: Page):
    page.goto(BASE_URL)
    wait_for_products_loaded(page)

    first_page = [p.strip() for p in page.locator(".card-title").all_inner_texts() if p.strip()]
    assert len(first_page) > 0, "Page 1 has no products loaded"

    next_btn = page.locator('[aria-label="Next"], ul.pagination li:last-child a').first
    expect(next_btn).to_be_visible(timeout=TIMEOUT)
    expect(next_btn).to_be_enabled(timeout=TIMEOUT)

    next_btn.click()

    
    expect(page.locator(".card-title").first).not_to_have_text(first_page[0], timeout=TIMEOUT)

    second_page = [p.strip() for p in page.locator(".card-title").all_inner_texts() if p.strip()]
    assert len(second_page) > 0, "No products displayed on page 2"
    assert first_page != second_page, "Page 2 products are identical to Page 1"


def test_select_product_and_validate_details(page: Page):
    page.goto(BASE_URL)
    wait_for_products_loaded(page)

    first_card = page.locator(".card").first
    name_in_grid = first_card.locator(".card-title").inner_text().strip()

    first_card.click()
    page.wait_for_url("**/product/**", timeout=TIMEOUT)

    detail_title = page.locator('[data-test="product-name"]')
    expect(detail_title).to_be_visible(timeout=TIMEOUT)
    expect(detail_title).to_have_text(name_in_grid, timeout=TIMEOUT)