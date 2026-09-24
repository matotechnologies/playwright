import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:4201/web/index.php/auth/login";
const USERNAME = "Admin";
const PASSWORD = "Admin@123098";

test("OrangeHRM Employee CRUD", async ({ page }) => {
    const employeeId = "EMP" + Math.floor(1000 + Math.random() * 9000);

    const firstName = "vasu";
    const lastName = "dev";
    const updatedFirstName = "vasudevan";
    const updatedLastName = "c";

    await page.goto(BASE_URL);

    await page.getByPlaceholder("Username").fill(USERNAME);
    await page.getByPlaceholder("Password").fill(PASSWORD);
    await page.getByRole("button", { name: "Login" }).click();

    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

    console.log("Login successful");

    await page.getByText("PIM", { exact: true }).click();
    await page.getByRole("link", { name: "Add Employee" }).click();

    await expect(page.getByRole("heading", { name: "Add Employee" })).toBeVisible();

    console.log("Add Employee page opened");

    await page.getByPlaceholder("First Name").fill(firstName);
    await page.getByPlaceholder("Last Name").fill(lastName);

    const employeeIdInput = page
        .locator(".oxd-input-group")
        .filter({ hasText: "Employee Id" })
        .locator("input");

    await employeeIdInput.fill(employeeId);

    await page.locator('input[type="file"]').setInputFiles("images/kohli.jpg");
    await page.getByRole("button", { name: "Save" }).click();

    await expect(page.getByText("Successfully Saved")).toBeVisible();

    console.log("Employee created successfully");

    await page.getByText("Employee List", { exact: true }).click();

    await expect(
        page.getByRole("heading", { name: "Employee Information" })
    ).toBeVisible();

    console.log("Employee List opened");

    const employeeIdSearch = page
        .locator(".oxd-input-group")
        .filter({ hasText: "Employee Id" })
        .locator("input");

    await employeeIdSearch.fill(employeeId);
    await page.getByRole("button", { name: "Search" }).click();

    await expect(
        page.getByText(employeeId, { exact: true })
    ).toBeVisible();

    console.log("Employee found using Employee ID");

    await page.getByText(employeeId, { exact: true }).click();

    await expect(
        page.getByRole("heading", { name: "Personal Details" })
    ).toBeVisible();

    console.log("Employee details opened");

    const firstNameField = page.locator('input[name="firstName"]');
    const lastNameField = page.locator('input[name="lastName"]');

    await firstNameField.fill(updatedFirstName);
    await lastNameField.fill(updatedLastName);

    console.log("First name after fill:", await firstNameField.inputValue());
    console.log("Last name after fill:", await lastNameField.inputValue());

    await expect(firstNameField).toHaveValue(updatedFirstName);
    await expect(lastNameField).toHaveValue(updatedLastName);

    await page.getByRole("button", { name: "Save" }).click();

    await expect(page.getByText("Successfully Updated")).toBeVisible();

    console.log("Employee updated successfully");

    await page.getByText("Employee List", { exact: true }).click();

    const employeeIdSearchAgain = page
        .locator(".oxd-input-group")
        .filter({ hasText: "Employee Id" })
        .locator("input");

    await employeeIdSearchAgain.fill(employeeId);
    await page.getByRole("button", { name: "Search" }).click();

    await expect(
        page.getByText(employeeId, { exact: true })
    ).toBeVisible();

    const row = page
        .locator(".oxd-table-row")
        .filter({ hasText: employeeId });

    await row.locator(".bi-trash").click();

    await expect(
        page.getByText("Are you Sure?", { exact: false })
    ).toBeVisible();

    console.log("Delete confirmation displayed");

    await page.getByRole("button", { name: "Yes, Delete" }).click();

    await expect(
        page.getByText("Successfully Deleted")
    ).toBeVisible();

    console.log("Employee deleted successfully");
});