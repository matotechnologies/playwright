import { chromium } from "@playwright/test";

const BASE_URL = "http://localhost:4201";
const USERNAME = "ohrmuser";
const PASSWORD = "Vasu31.7.4";


    const browser = await chromium.launch({ headless: True });
    const page = await browser.newPage();

    const employee_id = "EMP" + Math.floor(1000 + Math.random() * 9000);
    const first_name = "jackie";
    const last_name = "dev";
    const updated_first_name = "vasudevan";
    const updated_last_name = "c";

    // 1. Login to OrangeHRM
    await page.goto(BASE_URL);

    await page.getByPlaceholder("Username").fill("ohrmuser");
    await page.getByPlaceholder("Password").fill("Vasu31.7.4");
    await page.getByRole("button", { name: "Login" }).click();
    await page.getByRole("heading", { name: "Dashboard" }).waitFor();
    console.log("Login successful");

    // 2. Navigate to PIM → Add Employee
    await page.getByText("PIM", { exact: true }).click();
    await page.getByRole("link", { name: "Add Employee" }).click();

    await page.getByRole("heading", { name: "Add Employee" }).waitFor();
    console.log("Add Employee page opened");

    // 3. Create a new employee with valid details
    await page.getByPlaceholder("First Name").fill(first_name);
    await page.getByPlaceholder("Last Name").fill(last_name);

    const employee_id_input = page
        .locator(".oxd-input-group")
        .filter({ hasText: "Employee Id" })
        .locator("input");

    await employee_id_input.fill(employee_id);

    await page.locator('input[type="file"]').setInputFiles("images/kohli.jpg");

    await page.getByRole("button", { name: "Save" }).click();

    // 4. Verify the employee is created successfully
    await page.getByText("Successfully Saved").waitFor();
    console.log("Employee created successfully");

    // 5. Navigate to Employee List
    await page.getByText("Employee List", { exact: true }).click();

    await page.getByRole("heading", { name: "Employee Information" }).waitFor();
    console.log("Employee List opened");

    // 6. Search for the created employee using Employee ID
    const employee_id_search = page
        .locator(".oxd-input-group")
        .filter({ hasText: "Employee Id" })
        .locator("input");

    await employee_id_search.fill(employee_id);

    await page.getByRole("button", { name: "Search" }).click();

    // 7. Verify the employee appears in the search results
    await page.getByText(employee_id, { exact: true }).waitFor();
    console.log("Employee found using Employee ID");

    // 8. Open the employee details
    await page.getByText(employee_id, { exact: true }).click();

    await page.getByRole("heading", { name: "Personal Details" }).waitFor();
    console.log("Employee details opened");

    // 9. Edit the employee's first name and last name
    const first_name_field = page.locator('input[name="firstName"]');
    const last_name_field = page.locator('input[name="lastName"]');

    await first_name_field.fill(updated_first_name);
    await last_name_field.fill(updated_last_name);

    console.log("First name after fill:", await first_name_field.inputValue());
    console.log("Last name after fill:", await last_name_field.inputValue());

    // Save
    await page.getByRole("button", { name: "Save" }).click();

    console.log("Save clicked");
    console.log("Employee updated successfully");

    // Verify save was successful
    await page.getByText("Successfully Updated").waitFor();

    // 14. Delete the employee
    await page.getByText("Employee List", { exact: true }).click();

    const employee_id_search_2 = page
        .locator(".oxd-input-group")
        .filter({ hasText: "Employee Id" })
        .locator("input");

    await employee_id_search_2.fill(employee_id);
    await page.getByRole("button", { name: "Search" }).click();

    await page.getByText(employee_id, { exact: true }).waitFor();

    // Select employee
    const row = page.locator(".oxd-table-row").filter({ hasText: employee_id });
    await row.locator(".bi-trash").click();

    // 15. Verify delete confirmation message/dialog
    await page.getByText("Are you Sure?", { exact: false }).waitFor();

    console.log("Delete confirmation displayed");

    // 16. Confirm the deletion
    await page.getByRole("button", { name: "Yes, Delete" }).click();

    await page.getByText("Successfully Deleted").waitFor();
    console.log("Employee deleted successfully");

    // 17. Search for the deleted employee again
    const employee_id_search_3 = page
        .locator(".oxd-input-group")
        .filter({ hasText: "Employee Id" })
        .locator("input");

    await employee_id_search_3.fill(employee_id);
    await page.getByRole("button", { name: "Search" }).click();

    // 18. Verify the deleted employee is no longer displayed
    await page.getByText("No Records Found").waitFor();

    console.log("Deleted employee is no longer displayed");

    await browser.close();
