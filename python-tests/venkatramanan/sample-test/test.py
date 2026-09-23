import re
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:4201/web/index.php/auth/login"

def test_orangehrm_login_and_dashboard(page: Page):
    # 1. Open the login route directly and wait for scripts to load
    page.goto(BASE_URL, wait_until="networkidle")

    # 2. Selectors using stable HTML attributes
    username_input = page.locator("input[name='username']")
    password_input = page.locator("input[name='password']")
    submit_button = page.locator("button[type='submit']")

    expect(username_input).to_be_visible(timeout=15000)

    # 3. Enter credentials and submit
    username_input.fill("Admin")
    password_input.fill("admin123")
    submit_button.click()

    # 4. Verify successful transition to Dashboard
    expect(page).to_have_url(re.compile(r".*/dashboard/index.*"), timeout=30000)
    
    # 5. Verify the dashboard header renders
    header_title = page.locator("header h6")
    expect(header_title).to_be_visible(timeout=10000)
    expect(header_title).to_have_text("Dashboard")