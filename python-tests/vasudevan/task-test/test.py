from playwright.sync_api import Page, expect

def test_toolshop_smoke(page: Page):
    page.goto("http://localhost:4200")
    expect(page).to_have_title("Practice Software Testing - Toolshop - v5.0")
    
