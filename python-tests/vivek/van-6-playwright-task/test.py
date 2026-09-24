import os
from playwright.sync_api import sync_playwright, expect


BASE_URL = "http://localhost:4201"
USERNAME = "Admin"
PASSWORD = "Admin@123098"


def test_update_employee_job_details():

    with sync_playwright() as p:

        # 1. Open OrangeHRM
        browser = p.chromium.launch(headless=os.getenv("CI") == "true")
        page = browser.new_page()

        page.goto(BASE_URL)
        print("Current URL:", page.url)
        print("Page title:", page.title())
        print("Page content:", page.locator("body").inner_text())

        # 2. Login to OrangeHRM
        page.get_by_placeholder("Username").wait_for(state="visible")
        page.get_by_placeholder("Username").fill(USERNAME)
        page.get_by_placeholder("Password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

        # 3. Navigate to PIM
        page.get_by_role("link", name="PIM").click()

        # 5. Search for employee using Employee ID
        page.locator("input").nth(1).fill("0001")

        page.get_by_role("button", name="Search").click()

        # 6. Open the employee profile
        page.get_by_role("row").filter(has_text="0001").click()

        # 7. Open the Job section
        page.get_by_text("Job", exact=True).click()
        
        print("URL after opening Job:", page.url)
        print("Page content after opening Job:")
        print(page.locator("body").inner_text())
        
        selects = page.locator(".oxd-select-text")
        print("Select count:", selects.count())
        
        for i in range(selects.count()):
            print("Select", i, "text:", repr(selects.nth(i).inner_text()))

        # 8. Inspect Job dropdowns
        selects = page.locator(".oxd-select-text")
        
        print("Select count:", selects.count())
        
        for i in range(selects.count()):
            print(
                "Select",
                i,
                "text:",
                repr(selects.nth(i).inner_text())
            )
        
        # 9. Open the first dropdown
        selects.nth(0).click()
        
        options = page.locator(".oxd-select-option")
        
        print("Option count:", options.count())
        
        for i in range(options.count()):
            print(
                "Option",
                i,
                ":",
                repr(options.nth(i).inner_text())
            )

        # 10. Select Job Category
        page.locator(".oxd-select-text").nth(2).click()
        page.locator(".oxd-select-option").nth(1).click()

        # 11. Select Department
        page.locator(".oxd-select-text").nth(3).click()
        page.locator(".oxd-select-option").nth(1).click()

        # 12. Select Location
        page.locator(".oxd-select-text").nth(4).click()
        page.locator(".oxd-select-option").nth(1).click()

        # 13. Save the job details
        page.get_by_role("button", name="Save").click()

        # 14. Verify successful update
        expect(page.get_by_text("Successfully Updated")).to_be_visible()

        # 15. Verify job details are displayed
        for i in range(5):
            expect(page.locator(".oxd-select-text").nth(i)).not_to_have_text("")

        # 16. Refresh the page
        page.reload()

        # 17. Verify job details persist after refresh
        for i in range(5):
            expect(page.locator(".oxd-select-text").nth(i)).not_to_have_text("")

        browser.close()

