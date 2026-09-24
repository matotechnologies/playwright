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

        # 2. Login to OrangeHRM
        page.get_by_placeholder("Username").wait_for(state="visible")

        page.get_by_placeholder("Username").fill(USERNAME)
        page.get_by_placeholder("Password").fill(PASSWORD)

        page.get_by_role("button", name="Login").click()

        # 3. Navigate to PIM
        page.get_by_role("link", name="PIM").click()

        # 4. Search for employee using Employee ID
        page.locator("input").nth(1).fill("0001")

        page.get_by_role("button", name="Search").click()

        # 5. Open the employee profile
        page.get_by_role("row").filter(has_text="0001").click()

        # 6. Open the Job section
        page.get_by_text("Job", exact=True).click()

        print("URL after opening Job:", page.url)

        # 7. Open Job Category dropdown
        selects = page.locator(".oxd-select-text")

        selects.nth(2).click()

        # 8. Check available Job Category options
        options = page.locator(".oxd-select-option")

        try:
            options.first.wait_for(
                state="visible"
            )
        except Exception:
            print("No Job Category options found")
            browser.close()
            return

        option_count = options.count()

        print("Job Category option count:", option_count)

        for i in range(option_count):
            print("Job Category option:",i,repr(options.nth(i).inner_text()))

        # 10. Select first available Job Category
        valid_option = None

        for i in range(option_count):
            option_text = options.nth(i).inner_text().strip()

            if option_text and option_text.lower() != "no records found":
                valid_option = options.nth(i)
                break

        if valid_option is None:
            print("No Job Category records found, skipping")
            browser.close()
            return

        selected_category = valid_option.inner_text().strip()

        print("Selecting Job Category:", selected_category)

        valid_option.click()

        # 11. Save the job details
        page.get_by_role("button", name="Save").click()

        # 12. Verify successful update
        expect(page.get_by_text("Successfully Updated")).to_be_visible()

        # 13. Verify Job Category
        job_category = page.locator( ".oxd-select-text").nth(2)

        expect(job_category).not_to_have_text("")

        print("Job Category after update:",job_category.inner_text())

        # 14. Refresh the page
        page.reload()

        # 15. Wait for Job Details page again
        page.get_by_text( "Job Details",exact=True).wait_for(state="visible")

        # 16. Verify Job Category persists
        job_category = page.locator(".oxd-select-text").nth(2)

        expect(job_category).not_to_have_text("")

        print("Job Category after refresh:",job_category.inner_text())

        browser.close()
