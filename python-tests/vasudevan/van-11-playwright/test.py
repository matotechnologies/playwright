import random

from playwright.sync_api import Page, expect, sync_playwright
import pytest

BASE_URL = "http://localhost:4201/web/index.php/auth/login"
USERNAME = "Admin"
PASSWORD = "Admin@123098"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    employee_id = "EMP" + str(random.randint(1000, 9999))
    first_name = "jackie"
    last_name = "dev"
    updated_first_name = "vasudevan"
    updated_last_name = "c"

    # 1. Login to OrangeHRM
    page.goto(BASE_URL)

    page.get_by_placeholder("Username").fill("Admin")
    page.get_by_placeholder("Password").fill("Admin@123098")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
    print("Login successful")

    

    # 2. Navigate to PIM → Add Employee
    page.get_by_text("PIM", exact=True).click()
    page.get_by_role("link", name="Add Employee").click()

    expect(page.get_by_role("heading", name="Add Employee")).to_be_visible()
    print("Add Employee page opened")

    # 3. Create a new employee with valid details
    page.get_by_placeholder("First Name").fill(first_name)
    page.get_by_placeholder("Last Name").fill(last_name)

    employee_id_input = (
    page.locator(".oxd-input-group")
    .filter(has_text="Employee Id")
    .locator("input")
)
    employee_id_input.fill(employee_id)

    page.locator('input[type="file"]').set_input_files("images/kohli.jpg")
    page.get_by_role("button", name="Save").click()

    # 4. Verify the employee is created successfully
    expect(page.get_by_text("Successfully Saved")).to_be_visible()
    print("Employee created successfully")

    # 5. Navigate to Employee List
    page.get_by_text("Employee List", exact=True).click()

    expect(page.get_by_role("heading", name="Employee Information")).to_be_visible()
    print("Employee List opened")

    # 6. Search for the created employee using Employee ID
    employee_id_search = (
    page.locator(".oxd-input-group")
    .filter(has_text="Employee Id")
    .locator("input")
)

    employee_id_search.fill(employee_id)

    page.get_by_role("button", name="Search").click()

    # 7. Verify the employee appears in the search results
    expect(page.get_by_text(employee_id, exact=True)).to_be_visible()
    print("Employee found using Employee ID")

    # 8. Open the employee details
    page.get_by_text(employee_id, exact=True).click()

    expect(page.get_by_role("heading", name="Personal Details")).to_be_visible()
    print("Employee details opened")

    # 9. Edit the employee's first name and last name

    first_name_field = page.locator('input[name="firstName"]')
    last_name_field = page.locator('input[name="lastName"]')

    first_name_field.fill(updated_first_name)
    last_name_field.fill(updated_last_name)

    print("First name after fill:", first_name_field.input_value())
    print("Last name after fill:", last_name_field.input_value())

    expect(first_name_field).to_have_value(updated_first_name)
    expect(last_name_field).to_have_value(updated_last_name)

    # Save
    page.get_by_role("button", name="Save").click()

    print("Save clicked")
    print("Employee updated successfully")

    # Verify save was successful
    expect(page.get_by_text("Successfully Updated")).to_be_visible()


    # 14. Delete the employee
    page.get_by_text("Employee List", exact=True).click()

    employee_id_search = (
    page.locator(".oxd-input-group")
    .filter(has_text="Employee Id")
    .locator("input")
)

    employee_id_search.fill(employee_id)
    page.get_by_role("button", name="Search").click()

    expect(page.get_by_text(employee_id, exact=True)).to_be_visible()

    # Select employee
    row = page.locator(".oxd-table-row").filter(has_text=employee_id)
    row.locator(".bi-trash").click()


    # 15. Verify delete confirmation message/dialog
    expect(
        page.get_by_text("Are you Sure?", exact=False)
    ).to_be_visible()

    print("Delete confirmation displayed")
    

    # 16. Confirm the deletion
    page.get_by_role("button", name="Yes, Delete").click()

    expect(page.get_by_text("Successfully Deleted")).to_be_visible()
    print("Employee deleted successfully")


    browser.close()
