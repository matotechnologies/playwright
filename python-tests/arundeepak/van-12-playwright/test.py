import random
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

BASE_URL = "http://localhost:4201/web/index.php/auth/login"
USERNAME = "Admin"
PASSWORD = "Admin@123098"
IMAGE_PATH = Path(__file__).parent / "images" / "PNG1.jpg"

def test_create_employee():
    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        employee_id = "EMP" + str(random.randint(1000, 9999))
        first_name = "Arun"
        last_name = "Deepak"

        page.goto(BASE_URL)

        page.get_by_placeholder("Username").fill(USERNAME)

        page.get_by_placeholder("Password").fill(PASSWORD)

        page.get_by_role("button", name="Login").click()

        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        print("Login successful")

        page.get_by_role("link", name="PIM").click()

        page.get_by_role("link", name="Add Employee").click()

        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()

        print("Add Employee page opened")

        page.get_by_placeholder("First Name").fill(first_name)

        page.get_by_placeholder("Last Name").fill(last_name)

        employee_id_input = page.locator(".oxd-input-group").filter(has_text="Employee Id").locator("input")

        employee_id_input.fill(employee_id)

        page.locator('input[type="file"]').set_input_files(IMAGE_PATH)

        page.get_by_role("button", name="Save").click()

        expect(page.get_by_text("Successfully Saved")).to_be_visible()

        print("Employee created successfully")

        page.get_by_text("Employee List", exact=True).click()

        expect(page.get_by_role("heading", name="Employee Information")).to_be_visible()

        print("Employee List opened")

        employee_id_search = page.locator(".oxd-input-group").filter(has_text="Employee Id").locator("input")

        employee_id_search.fill(employee_id)

        page.get_by_role("button", name="Search").click()

        expect(page.get_by_text(employee_id, exact=True)).to_be_visible()

        print("Employee found using Employee ID")

        employee_row = page.locator(".oxd-table-row").filter(has_text=employee_id)

        expect(employee_row.get_by_text(first_name, exact=True)).to_be_visible()

        expect(employee_row.get_by_text(last_name, exact=True)).to_be_visible()

        print("Employee details verified")

        page.get_by_role("link", name="PIM").click()

        page.get_by_role("link", name="Add Employee").click()

        expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()

        page.get_by_placeholder("First Name").fill("Duplicate")

        page.get_by_placeholder("Last Name").fill("Employee")

        duplicate_employee_id = page.locator(".oxd-input-group").filter(has_text="Employee Id").locator("input")

        duplicate_employee_id.fill(employee_id)

        page.get_by_role("button", name="Save").click()

        expect(page.get_by_text("Employee Id already exists", exact=False)).to_be_visible()

        print("Duplicate Employee ID rejected")

        page.get_by_text("Employee List", exact=True).click()

        expect(page.get_by_role("heading", name="Employee Information")).to_be_visible()

        employee_id_search = page.locator(".oxd-input-group").filter(has_text="Employee Id").locator("input")

        employee_id_search.fill(employee_id)

        page.get_by_role("button", name="Search").click()

        employee_row = page.locator(".oxd-table-row").filter(has_text=employee_id)

        expect(employee_row.get_by_text(employee_id, exact=True)).to_be_visible()

        expect(employee_row.get_by_text(first_name, exact=True)).to_be_visible()

        expect(employee_row.get_by_text(last_name, exact=True)).to_be_visible()

        print("Employee details verified before refresh")

        page.reload()

        employee_id_search = page.locator(".oxd-input-group").filter(has_text="Employee Id").locator("input")

        employee_id_search.fill(employee_id)

        page.get_by_role("button", name="Search").click()

        employee_row = page.locator(".oxd-table-row").filter(has_text=employee_id)

        expect(employee_row.get_by_text(employee_id, exact=True)).to_be_visible()

        expect(employee_row.get_by_text(first_name, exact=True)).to_be_visible()

        expect(employee_row.get_by_text(last_name, exact=True)).to_be_visible()

        print("Employee details persist after refresh")
        
        browser.close()