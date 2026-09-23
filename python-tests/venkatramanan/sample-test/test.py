import re
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:4201/web/index.php/auth/login"
USERNAME = "Admin"
PASSWORD = "Admin@123098"


def test_update_employee_job_details(page: Page):
    # 1. Open login page directly
    page.goto(BASE_URL, wait_until="networkidle")

    # 2. Login
    page.locator("input[name='username']").fill(USERNAME)
    page.locator("input[name='password']").fill(PASSWORD)
    page.locator("button[type='submit']").click()

    # Confirm dashboard is reached
    expect(page).to_have_url(re.compile(r".*/dashboard/index.*"), timeout=30000)

    # 3. Navigate to PIM
    page.get_by_role("link", name="PIM").click()
    page.wait_for_url("**/pim/viewEmployeeList**")

    # 4. Open the first available employee profile (avoids hardcoding '0001')
    first_employee = page.locator(".oxd-table-body .oxd-table-row").first
    expect(first_employee).to_be_visible(timeout=15000)
    first_employee.click()

    # 5. Open the Job section
    job_tab = page.get_by_role("link", name="Job")
    expect(job_tab).to_be_visible(timeout=10000)
    job_tab.click()
    page.wait_for_url("**/pim/viewJobDetails/empNumber/**")

    # 6. Update the first dropdown (Job Title)
    job_title_dropdown = page.locator(".oxd-select-text").first
    job_title_dropdown.click()
    
    # Wait for the dropdown options overlay to appear and click the first valid option
    option = page.locator(".oxd-select-dropdown .oxd-select-option").nth(1)
    expect(option).to_be_visible(timeout=5000)
    option.click()

    # 7. Save job details (Scoped to avoid strict mode violations)
    save_btn = page.locator("form").filter(has_text="Joined Date").get_by_role("button", name="Save")
    if save_btn.is_visible():
        save_btn.click()
    else:
        page.locator("button[type='submit']").first.click()

    # 8. Verify success toast notification
    expect(page.locator(".oxd-toast--success")).to_be_visible(timeout=10000)

    # 9. Reload and verify selected value persisted
    page.reload(wait_until="networkidle")
    expect(page.locator(".oxd-select-text").first).not_to_have_text("-- Select --")