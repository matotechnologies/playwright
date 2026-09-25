import os
import re
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:4200"

def test_toolshop_cart_checkout():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.getenv("CI") == "true")
        page = browser.new_page()

        # 1. Open Toolshop locally
        page.goto(BASE_URL)
        expect(page).to_have_title("Practice Software Testing - Toolshop - v5.0")
        print("Toolshop opened successfully")

        # 2. Select multiple available products dynamically 
        product_cards = page.locator("a[href^='/product/']")
        expect(product_cards.first).to_be_visible()
        product_count = product_cards.count()
        print("Products found:", product_count)

        selected_products = []

        for i in range(product_count):
            product = product_cards.nth(i)
            product_name = product.inner_text().strip()

            if "Out of stock" in product_name:
                print("Skipping unavailable product")
                continue

            product_url = product.get_attribute("href")

            selected_products.append({
                "name": product_name.split("\n")[0],
                "url": product_url
            })

            print(f"Selected product: {product_name.split(chr(10))[0]}")

            if len(selected_products) == 2:
                break

        assert len(selected_products) == 2, \
            "Less than two available products were found"

        # 3. Add products to cart
        selected_product_data = []

        for product_info in selected_products:
            page.goto(BASE_URL)

            product_cards = page.locator("a[href^='/product/']")
            expect(product_cards.first).to_be_visible()

            product_link = page.locator(f"a[href='{product_info['url']}']")
            expect(product_link).to_be_visible()

            print(f"Opening product: {product_info['name']}")

            product_link.click()

            product_name_locator = page.locator("h1")
            expect(product_name_locator).to_be_visible()

            product_name = product_name_locator.inner_text().strip()

            price_text = page.locator("text=/\\$\\d+\\.\\d+/").first.inner_text()
            price = float(price_text.replace("$", "").strip())

            print(f"Product: {product_name} , Price: ${price:.2f}")

            add_to_cart_button = page.get_by_role("button", name="Add to cart")
            expect(add_to_cart_button).to_be_visible()
            add_to_cart_button.click()

            cart_link = page.locator("a[href='/checkout']")
            expected_cart_count = len(selected_product_data) + 1

            expect(cart_link).to_contain_text(str(expected_cart_count))

            print(f"Added to cart: {product_name} | Cart count: {expected_cart_count}")

            selected_product_data.append({
                "name": product_name,
                "price": price,
                "quantity": 1
            })

        # 4. Open cart
        cart_link = page.get_by_role("link", name="Cart")
        expect(cart_link).to_be_visible()
        cart_link.click()

        expect(page.locator("table")).to_be_visible()
        print("Cart opened")

        # 5. Validate cart contents
        cart_table = page.locator("table")

        for product in selected_product_data:
            product_row = cart_table.locator("tr").filter(has_text=product["name"]).first
            expect(product_row).to_be_visible()
            print(f"Verified in cart: {product['name']}")

        print("All selected products are present in the cart")

        # 6. Validate individual product prices
        expected_subtotal = 0

        product_rows = cart_table.locator("tbody").first.locator("tr")
        row_count = product_rows.count()

        print(f"Product rows found in cart: {row_count}")

        for product in selected_product_data:
            product_name = product["name"]
            expected_price = product["price"]
            quantity = product["quantity"]
            matching_row = None

            for i in range(row_count):
                row = product_rows.nth(i)
                first_cell = row.locator("td").first
                cell_text = first_cell.inner_text().strip()

                if cell_text == product_name:
                    matching_row = row
                    break

            assert matching_row is not None, \
                f"Product row not found for {product_name}"
            expect(matching_row).to_be_visible()
            row_text = matching_row.inner_text()
            print(f"Cart details for {product_name}: {row_text.strip()}")
            price_matches = re.findall(r"\$(\d+\.\d+)", row_text)
            assert len(price_matches) >= 2, \
                f"Expected product price and total price for {product_name}"
            cart_price = float(price_matches[0])
            row_total = float(price_matches[-1])
            assert cart_price == expected_price, \
                f"Price mismatch for {product_name}: Expected ${expected_price:.2f}, but found ${cart_price:.2f}"
            print(f"Price verified: {product_name} = ${cart_price:.2f}")
            expected_row_total = expected_price * quantity
            assert row_total == expected_row_total, \
                f"Total mismatch for {product_name}: Expected ${expected_row_total:.2f}, but found ${row_total:.2f}"
            print(f"Product total verified: {product_name} = ${row_total:.2f}")
            expected_subtotal += expected_row_total
        print(f"Expected subtotal: ${expected_subtotal:.2f}")

        # 7. Modify product quantity
        print("Modifying product quantities")

        first_product = selected_product_data[0]
        product_name = first_product["name"]

        quantity_input = page.get_by_role("spinbutton", name=f"Quantity for {product_name}")

        expect(quantity_input).to_be_visible()

        quantity_input.fill("2")
        quantity_input.press("Enter")

        expect(quantity_input).to_have_value("2")

        first_product["quantity"] = 2

        updated_expected_subtotal = 0

        for product in selected_product_data:
            updated_expected_subtotal += product["price"] * product["quantity"]

        print(f"Updated expected subtotal: ${updated_expected_subtotal:.2f}")

        # 8. Recalculate expected subtotal
        expected_subtotal = 0

        for product in selected_product_data:
            product_name = product["name"]
            quantity = product["quantity"]
            price = product["price"]

            expected_subtotal += price * quantity

        print(f"Expected subtotal after quantity update: ${expected_subtotal:.2f}")

        # 9. Compare expected subtotal with application
        cart_rows = cart_table.locator("tr")
        total_row = None

        for i in range(cart_rows.count()):
            row = cart_rows.nth(i)
            row_text = row.inner_text().strip()

            if row_text.startswith("Total"):
                total_row = row
                break

        assert total_row is not None, \
            "Cart total row was not found"

        expect(total_row).to_be_visible()
        expect(total_row).to_contain_text(f"${updated_expected_subtotal:.2f}")

        total_text = total_row.inner_text()

        total_matches = re.findall(r"\$(\d+\.\d+)", total_text)

        assert len(total_matches) >= 1, \
            "Cart subtotal was not found"

        application_subtotal = float(total_matches[-1])

        print(f"Application subtotal: ${application_subtotal:.2f}")

        assert round(updated_expected_subtotal, 2) == round(application_subtotal, 2), \
            f"Subtotal mismatch: Expected ${updated_expected_subtotal:.2f}, but application shows ${application_subtotal:.2f}"

        print("Subtotal verified successfully")

        # 10. Remove a product
        print("Removing a product")

        product_to_remove = selected_product_data[0]
        product_name = product_to_remove["name"]

        product_rows = cart_table.locator("tbody").first.locator("tr")
        matching_row = None

        for i in range(product_rows.count()):
            row = product_rows.nth(i)
            first_cell = row.locator("td").first
            cell_text = first_cell.inner_text().strip()

            if cell_text == product_name:
                matching_row = row
                break

        assert matching_row is not None, \
            f"Product row not found for {product_name}"

        expect(matching_row).to_be_visible()

        print(f"Product selected for removal: {product_name}")

        remove_link = matching_row.locator("a.btn.btn-danger")

        expect(remove_link).to_be_visible()
        remove_link.click()

        expect(cart_table.locator("tbody").first.locator("tr").filter(has_text=product_name)).to_have_count(0)
        print(f"Product removed successfully: {product_name}")

        # 11. Calculate expected subtotal after removal
        expected_updated_subtotal = 0

        for product in selected_product_data:
            if product["name"] == product_name:
                continue

            expected_updated_subtotal += product["price"] * product["quantity"]

        print(f"Expected subtotal after removing {product_name}: "f"${expected_updated_subtotal:.2f}")

        # 12. Validate updated application total
        cart_rows = cart_table.locator("tr")
        total_row = None

        for i in range(cart_rows.count()):
            row = cart_rows.nth(i)
            row_text = row.inner_text().strip()

            if row_text.startswith("Total"):
                total_row = row
                break

        assert total_row is not None, \
            "Cart total row was not found"

        expect(total_row).to_be_visible()
        expect(total_row).to_contain_text(f"${expected_updated_subtotal:.2f}")

        updated_total_text = total_row.inner_text()

        updated_total_matches = re.findall(
            r"\$(\d+\.\d+)",
            updated_total_text
        )

        assert len(updated_total_matches) >= 1, \
            "Updated cart total was not found"

        updated_application_total = float(updated_total_matches[-1])

        print(f"Expected updated total: ${expected_updated_subtotal:.2f}")
        print(f"Application updated total: ${updated_application_total:.2f}")

        assert round(expected_updated_subtotal, 2) == round(updated_application_total, 2), \
            f"Updated total mismatch: Expected ${expected_updated_subtotal:.2f}, but application shows ${updated_application_total:.2f}"

        print("Updated subtotal verified successfully")

        # 13. Reload page and verify cart state
        print("Reloading cart page")

        page.reload()
        page.wait_for_load_state("domcontentloaded")

        expect(page.locator("table")).to_be_visible()

        cart_table = page.locator("table")

        product_rows_after_reload = cart_table.locator("tbody").first.locator("tr")

        removed_product_found = False

        for i in range(product_rows_after_reload.count()):
            row = product_rows_after_reload.nth(i)
            first_cell = row.locator("td").first
            cell_text = first_cell.inner_text().strip()

            if cell_text == product_name:
                removed_product_found = True
                break

        assert not removed_product_found, \
            f"Removed product appeared after reload: {product_name}"

        print(
            f"Verified removed product is absent after reload: "
            f"{product_name}"
        )

        remaining_products = []

        for product in selected_product_data:
            if product["name"] == product_name:
                continue

            remaining_products.append(product)

        for product in remaining_products:
            product_name_after_reload = product["name"]
            product_found = False

            for i in range(product_rows_after_reload.count()):
                row = product_rows_after_reload.nth(i)
                first_cell = row.locator("td").first
                cell_text = first_cell.inner_text().strip()

                if cell_text == product_name_after_reload:
                    product_found = True
                    break

            assert product_found, \
                f"Remaining product missing after reload: {product_name_after_reload}"

            print(
                f"Verified product after reload: "
                f"{product_name_after_reload}"
            )

        print("Cart state verified successfully after reload")

        # 14. Continue to checkout
        page.get_by_role("button", name="Proceed to checkout").click()

        print("Checkout page opened")

        # 15. Validate mandatory checkout fields
        print("Validating mandatory checkout fields")

        checkout_forms = page.locator("form")

        expect(checkout_forms).to_have_count(4)

        print("Checkout forms verified: 4")

        visible_form = page.locator("form:visible").first

        expect(visible_form).to_be_visible()

        print("Visible checkout form found")

        visible_inputs = visible_form.locator("input:visible")
        input_count = visible_inputs.count()

        print(f"Visible input fields found: {input_count}")

        assert input_count > 0, \
            "No visible checkout input fields were found"


        email_field = visible_form.get_by_role("textbox", name="Email address *")
        password_field = visible_form.get_by_role("textbox", name="Password *")

        expect(email_field).to_be_visible()
        expect(password_field).to_be_visible()

        print("Mandatory email field is visible")
        print("Mandatory password field is visible")

        expect(email_field).to_have_value("")
        expect(password_field).to_have_value("")

        print("Mandatory checkout fields validated successfully")

        # 16. Complete checkout fields
        print("Completing checkout as guest")

        guest_tab = page.get_by_role("tab", name="Continue as Guest")

        expect(guest_tab).to_be_visible()

        guest_tab.click()

        print("Continue as Guest selected")

        guest_form = page.locator("form:visible").first

        expect(guest_form).to_be_visible()

        print("Guest checkout form opened")

        guest_email = guest_form.get_by_role("textbox", name="Email address *")
        guest_first_name = guest_form.get_by_role("textbox", name="First name *")
        guest_last_name = guest_form.get_by_role("textbox", name="Last name *")

        expect(guest_email).to_be_visible()
        expect(guest_first_name).to_be_visible()
        expect(guest_last_name).to_be_visible()

        guest_email.fill("vivek@example.com")
        guest_first_name.fill("Vivek")
        guest_last_name.fill("NP")

        expect(guest_email).to_have_value("vivek@example.com")
        expect(guest_first_name).to_have_value("Vivek")
        expect(guest_last_name).to_have_value("NP")

        print("Guest email entered")
        print("Guest first name entered")
        print("Guest last name entered")

        continue_guest_button = guest_form.get_by_role("button", name="Continue as Guest")

        expect(continue_guest_button).to_be_visible()

        continue_guest_button.click()

        print("Guest checkout details submitted")

        proceed_guest_button = page.locator("[data-test='proceed-2-guest']")

        expect(proceed_guest_button).to_be_visible()
        expect(proceed_guest_button).to_be_enabled()

        proceed_guest_button.click()

        print("Proceed to checkout clicked")
        print("Billing address page opened")

        billing_form = page.locator("form:visible").first

        expect(billing_form).to_be_visible()

        print("Billing address form opened")

        country = billing_form.get_by_role("combobox", name="Country")

        expect(country).to_be_visible()
        expect(country).to_be_enabled()

        print("Country field is visible")

        country.select_option(label="India")

        print("Country selected: India")

        postal_code = billing_form.get_by_placeholder("Your Postcode *")
        house_number = billing_form.get_by_placeholder("e.g. 42 *")
        street = billing_form.get_by_placeholder("Your Street *")
        city = billing_form.get_by_placeholder("Your City *")
        state = billing_form.get_by_placeholder("State *")

        expect(postal_code).to_be_visible()
        expect(house_number).to_be_visible()
        expect(street).to_be_visible()
        expect(city).to_be_visible()
        expect(state).to_be_visible()

        postal_code.fill("570001")
        house_number.fill("42")
        street.fill("Sayyaji Rao Road")
        city.fill("Mysore")
        state.fill("Karnataka")

        expect(postal_code).to_have_value("570001")
        expect(house_number).to_have_value("42")
        expect(street).to_have_value("Sayyaji Rao Road")
        expect(city).to_have_value("Mysore")
        expect(state).to_have_value("Karnataka")

        proceed_button = page.locator("[data-test='proceed-3']")

        expect(proceed_button).to_be_visible()
        expect(proceed_button).to_be_enabled()

        proceed_button.click()

        print("Proceed to payment clicked")
        print("Payment page opened")

        # 17. Select payment method
        print("Selecting payment method")

        payment_method = page.locator("[data-test='payment-method']")

        expect(payment_method).to_be_visible()
        expect(payment_method).to_be_enabled()

        payment_method.select_option(label="Cash on Delivery")

        expect(payment_method).to_have_value("cash-on-delivery")

        print("Payment method selected: Cash on Delivery")

        # 18. Complete checkout
        page.get_by_role("button", name="Confirm").click()

        # 19. Verify payment success
        print("Verifying payment success")

        payment_success_message = page.locator(
            "[data-test='payment-success-message']"
        )

        expect(payment_success_message).to_be_visible()

        expect(payment_success_message).to_have_text(
            "Payment was successful"
        )

        print("Payment successful message verified")

        browser.close()

