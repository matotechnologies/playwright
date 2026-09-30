import random
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:4200"
PASSWORD = "ArunDeepak*123"


def test_application_accessible(page: Page):

    page.goto(BASE_URL)

    expect(page.locator("#Layer_1")).to_be_visible()


def register_user(page: Page):

    email = f"arundeepak{random.randint(10000, 99999)}@example.com"

    page.goto(f"{BASE_URL}/auth/register")

    page.get_by_placeholder("First name *").fill("Arun")
    page.get_by_placeholder("Your last name *").fill("Deepak")
    page.get_by_placeholder("YYYY-MM-DD").fill("1999-01-01")

    page.locator("#country").select_option("IN")

    page.get_by_placeholder("Your Postcode *").fill("630606")
    page.get_by_placeholder("e.g. 42 *").fill("32-E")

    page.get_by_placeholder("Your Street *").fill("Main Street")
    page.get_by_placeholder("Your City *").fill("Manamadurai")
    page.get_by_placeholder("Your State *").fill("Tamil Nadu")

    page.locator("[data-test='phone']").fill("9876543210")

    page.get_by_placeholder("Your email *").fill(email)
    page.get_by_placeholder("Your password").fill(PASSWORD)

    page.locator("button[data-test='register-submit']").click()

    expect(page).to_have_url(f"{BASE_URL}/auth/login")

    print("REGISTER EMAIL:", email)

    return email


def login(page: Page, email):

    page.goto(f"{BASE_URL}/auth/login")

    page.get_by_placeholder("Your email").fill(email)
    page.get_by_placeholder("Your password").fill(PASSWORD)

    page.locator("input[data-test='login-submit']").click()

    expect(page).to_have_url(f"{BASE_URL}/account")


def test_session_persistence(page: Page):

    email = register_user(page)

    login(page, email)

    expect(page).to_have_url(f"{BASE_URL}/account")

    page.reload()

    expect(page).to_have_url(f"{BASE_URL}/account")


def test_new_browser_context(page: Page, browser):

    email = register_user(page)

    login(page, email)

    expect(page).to_have_url(f"{BASE_URL}/account")

    context = browser.new_context()
    new_page = context.new_page()

    new_page.goto(f"{BASE_URL}/account")

    expect(new_page).to_have_url(f"{BASE_URL}/auth/login")

    context.close()


def test_logout(page: Page):

    email = register_user(page)

    login(page, email)

    expect(page).to_have_url(f"{BASE_URL}/account")

    page.locator("[data-test='nav-menu']").click()

    page.locator("[data-test='nav-sign-out']").click()

    expect(page).to_have_url(f"{BASE_URL}/auth/login")


def test_invalid_login(page: Page):

    page.goto(f"{BASE_URL}/auth/login")

    page.get_by_placeholder("Your email").fill("invalid@example.com")
    page.get_by_placeholder("Your password").fill("WrongPassword*123")

    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(f"{BASE_URL}/auth/login")

    expect(page.get_by_text("Invalid email or password")).to_be_visible()


def test_required_fields(page: Page):

    page.goto(f"{BASE_URL}/auth/register")

    expect(page.get_by_placeholder("First name *")).to_have_attribute("aria-required", "true")

    expect(page.get_by_placeholder("Your last name *")).to_have_attribute("aria-required", "true")

    expect(page.get_by_placeholder("Your Postcode *")).to_have_attribute("aria-required", "true")

    expect(page.get_by_placeholder("Your email *")).to_have_attribute("aria-required", "true")


def test_authentication_storage(page: Page):

    email = register_user(page)

    login(page, email)

    expect(page).to_have_url(f"{BASE_URL}/account")

    cookies = page.context.cookies()

    local_storage = page.evaluate("Object.keys(localStorage)")

    session_storage = page.evaluate("Object.keys(sessionStorage)")

    print("Cookies:", cookies)
    print("Local Storage:", local_storage)
    print("Session Storage:", session_storage)

    assert (cookies or local_storage or session_storage), "No authentication/session state found after login"
