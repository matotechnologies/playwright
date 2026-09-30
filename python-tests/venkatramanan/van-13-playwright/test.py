import os
import re
import time
import pytest
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect

# ---------------------------------------------------------------- CONFIG
LOGIN_URL = os.getenv("OHRM_LOGIN_URL", "http://localhost:4201/web/index.php/auth/login")
BASE_URL = LOGIN_URL.split("/web/")[0]
ADMIN_USER = os.getenv("OHRM_ADMIN_USER", "Admin")
ADMIN_PASS = os.getenv("OHRM_ADMIN_PASS", "Admin@123098")
LEAVE_TYPE = os.getenv("OHRM_LEAVE_TYPE", "Casual Leave")
ENTITLEMENT = os.getenv("OHRM_ENTITLEMENT", "10")
HEADLESS = os.getenv("HEADLESS", "1") == "1"
REASON = "Family function - automation test"

SUF = str(int(time.time()))[-6:]
FIRST, LAST = "Auto", f"Emp{SUF}"
EMP_USER, EMP_PASS = f"auto{SUF}", "Xk9#mPq2$vLw"

expect.set_options(timeout=20000)
os.makedirs("screenshots", exist_ok=True)


class State:
    leave_type = LEAVE_TYPE
    leave_date = ""
    target_year = None


# ---------------------------------------------------------------- HELPERS
def shot(page, name):
    page.screenshot(path=f"screenshots/{name}.png")


def future_workday(days=14, year=None):
    d = date.today() + timedelta(days=days)
    if year:
        try:
            d = d.replace(year=year)
        except ValueError:
            d = date(year, d.month, 28)
    while d.weekday() >= 5:  # Skip Sat/Sun
        d += timedelta(days=1)
    return d


def field(page, label):
    return (
        page.locator(".oxd-input-group")
        .filter(has=page.locator("label", has_text=re.compile(rf"^\s*{re.escape(label)}", re.I)))
        .locator("input")
    )


def wait_for_server(page, url, retries=15, delay=3):
    for _ in range(retries):
        try:
            resp = page.goto(url, timeout=10000)
            if resp and resp.status < 400:
                return True
        except Exception:
            time.sleep(delay)
    return False


def login(page, user, pwd):
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    page.get_by_placeholder("Username").wait_for(state="visible", timeout=20000)
    page.get_by_placeholder("Username").fill(user)
    page.get_by_placeholder("Password").fill(pwd)
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile("dashboard"), timeout=20000)


def set_dates(page, d):
    inputs = page.locator(".oxd-date-input input")
    for i in range(inputs.count()):
        box = inputs.nth(i)
        box.click()
        box.press("Control+a")
        box.fill(d)
        box.press("Tab")
    page.locator("h5, h6").first.click()
    page.wait_for_timeout(500)


def apply_leave(page, d):
    page.goto(f"{BASE_URL}/web/index.php/leave/applyLeave")
    page.wait_for_load_state("networkidle")

    # 1. Select Leave Type
    page.locator(".oxd-select-text").first.click()
    page.locator(".oxd-select-dropdown").wait_for(state="visible", timeout=5000)

    options = page.locator(".oxd-select-dropdown .oxd-select-option:not(:has-text('-- Select --'))")
    matched = options.filter(has_text=re.compile(re.escape(State.leave_type), re.I))
    if matched.count() > 0:
        matched.first.click()
    else:
        options.first.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    # 2. Fill Dates and Reason
    set_dates(page, d)
    page.locator("textarea").fill(REASON)

    # 3. Click Apply
    page.locator("button[type='submit'], button:has-text('Apply')").first.click()


def filter_my_leave(page, d=None):
    page.goto(f"{BASE_URL}/web/index.php/leave/viewMyLeaveList")
    page.wait_for_load_state("networkidle")

    if d:
        set_dates(page, d)

    page.locator("button[type='submit'], button:has-text('Search')").first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)


# ---------------------------------------------------------------- FIXTURES
@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def admin_page(browser_instance):
    context = browser_instance.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="session")
def emp_page(browser_instance):
    context = browser_instance.new_context()
    page = context.new_page()
    yield page
    context.close()


# ---------------------------------------------------------------- TESTS
def test_setup_01_admin_login(admin_page):
    if not wait_for_server(admin_page, LOGIN_URL):
        pytest.fail(f"Could not connect to {LOGIN_URL}")
    login(admin_page, ADMIN_USER, ADMIN_PASS)


def test_setup_02_create_employee(admin_page):
    page = admin_page
    page.goto(f"{BASE_URL}/web/index.php/pim/addEmployee")
    page.get_by_placeholder("First Name").fill(FIRST)
    page.get_by_placeholder("Last Name").fill(LAST)
    page.locator(".oxd-switch-input").click()
    field(page, "Username").fill(EMP_USER)
    field(page, "Password").fill(EMP_PASS)
    field(page, "Confirm Password").fill(EMP_PASS)
    page.keyboard.press("Tab")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    for attempt in (1, 2):
        page.get_by_role("button", name="Save").click()
        try:
            page.wait_for_url(re.compile("viewPersonalDetails"), timeout=15000)
            return
        except Exception:
            shot(page, f"err_add_employee_try{attempt}")
            page.wait_for_timeout(2000)
    raise AssertionError("Employee was not created")


def test_setup_03_ensure_leave_type(admin_page):
    page = admin_page

    # 1. Define Leave Period
    page.goto(f"{BASE_URL}/web/index.php/leave/defineLeavePeriod")
    page.wait_for_load_state("networkidle")
    save_period_btn = page.locator("button[type='submit'], button:has-text('Save')").first
    if save_period_btn.is_visible():
        selects = page.locator(".oxd-select-text")
        for i in range(selects.count()):
            txt = selects.nth(i).inner_text().strip()
            if "-- Select --" in txt or not txt:
                selects.nth(i).click()
                page.locator(".oxd-select-dropdown .oxd-select-option:not(:has-text('-- Select --'))").first.click()
                page.wait_for_timeout(300)
        save_period_btn.click()
        page.wait_for_timeout(1500)

    # 2. Ensure Leave Type exists
    page.goto(f"{BASE_URL}/web/index.php/leave/leaveTypeList")
    page.wait_for_load_state("networkidle")

    if page.locator(".oxd-table-card", has_text=LEAVE_TYPE).count() == 0:
        add_btn = page.get_by_role("button", name="Add")
        if add_btn.is_visible():
            add_btn.click()
            page.wait_for_load_state("networkidle")
            name_input = page.locator(".oxd-input-group").filter(
                has=page.locator("label:has-text('Name')")
            ).locator("input")
            name_input.fill(LEAVE_TYPE)
            page.locator("button[type='submit']").click()
            page.wait_for_timeout(2000)


def test_setup_04_add_entitlement(admin_page):
    page = admin_page
    page.goto(f"{BASE_URL}/web/index.php/leave/addLeaveEntitlement")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # 1. Search employee using the unique LAST name
    hint_box = page.get_by_placeholder("Type for hints...")
    hint_box.wait_for(state="visible", timeout=10000)
    hint_box.click()
    hint_box.press_sequentially(LAST, delay=100)

    page.locator(".oxd-autocomplete-dropdown").wait_for(state="visible", timeout=10000)
    page.wait_for_selector(
        ".oxd-autocomplete-dropdown .oxd-autocomplete-option:not(:has-text('Searching'))",
        timeout=10000
    )

    options = page.locator(".oxd-autocomplete-dropdown .oxd-autocomplete-option")
    emp_opt = options.filter(has_text=LAST)
    if emp_opt.count() > 0:
        emp_opt.first.click()
    else:
        options.first.click()
    page.wait_for_timeout(500)

    # 2. Select Leave Type
    lt_group = page.locator(".oxd-input-group").filter(
        has=page.locator("label", has_text=re.compile(r"Leave Type", re.I))
    )
    lt_group.locator(".oxd-select-text").click()
    page.locator(".oxd-select-dropdown").wait_for(state="visible", timeout=5000)

    lt_options = page.locator(".oxd-select-dropdown .oxd-select-option:not(:has-text('-- Select --'))")
    matched_type = lt_options.filter(has_text=re.compile(re.escape(State.leave_type), re.I))
    if matched_type.count() > 0:
        State.leave_type = matched_type.first.inner_text().strip()
        matched_type.first.click()
    else:
        first_opt = lt_options.first
        State.leave_type = first_opt.inner_text().strip()
        first_opt.click()
    page.wait_for_timeout(500)

    # 3. Handle Leave Period
    period_group = page.locator(".oxd-input-group").filter(
        has=page.locator("label", has_text=re.compile(r"Leave Period", re.I))
    )
    if period_group.count() > 0:
        period_box = period_group.locator(".oxd-select-text")
        p_text = period_box.inner_text().strip()
        if "-- Select --" in p_text or not p_text:
            period_box.click()
            page.locator(".oxd-select-dropdown").wait_for(state="visible", timeout=5000)
            p_opt = page.locator(".oxd-select-dropdown .oxd-select-option:not(:has-text('-- Select --'))").first
            p_text = p_opt.inner_text().strip()
            p_opt.click()
            page.wait_for_timeout(500)

        ym = re.search(r"(\d{4})", p_text)
        if ym:
            State.target_year = int(ym.group(1))

    # 4. Fill Entitlement amount
    ent_group = page.locator(".oxd-input-group").filter(
        has=page.locator("label", has_text=re.compile(r"Entitlement", re.I))
    )
    ent_input = ent_group.locator("input")
    ent_input.click()
    ent_input.fill(str(ENTITLEMENT))

    # 5. Save and Confirm
    page.locator("button[type='submit']").click()
    try:
        confirm_btn = page.locator(".oxd-dialog-container-default").get_by_role("button", name="Confirm")
        confirm_btn.wait_for(state="visible", timeout=3000)
        confirm_btn.click()
    except Exception:
        pass

    page.wait_for_timeout(1500)
    try:
        page.wait_for_url(re.compile("viewLeaveEntitlements"), timeout=8000)
    except Exception:
        expect(page.locator(".oxd-toast")).to_be_visible(timeout=5000)
    shot(page, "00_admin_entitlement")


def test_step_01_employee_login(emp_page):
    login(emp_page, EMP_USER, EMP_PASS)


def test_step_02_check_balance(emp_page):
    page = emp_page
    page.goto(f"{BASE_URL}/web/index.php/leave/viewMyLeaveEntitlements")
    page.wait_for_load_state("networkidle")

    if not page.locator(".oxd-table-body").is_visible():
        page.goto(f"{BASE_URL}/web/index.php/leave/viewLeaveModule")
        ent_tab = page.locator(".oxd-topbar-body-nav-tab", has_text="Entitlements")
        if ent_tab.is_visible():
            ent_tab.click()
            page.get_by_text("My Entitlements", exact=True).click()
            page.wait_for_load_state("networkidle")

    expect(page.locator(".oxd-table-body")).to_be_visible(timeout=15000)
    body = page.locator(".oxd-table-body").inner_text()
    assert State.leave_type in body and str(ENTITLEMENT) in body
    shot(page, "01_balance")


def test_step_03_to_06_apply_leave(emp_page):
    page = emp_page
    page.goto(f"{BASE_URL}/web/index.php/leave/applyLeave")
    page.wait_for_load_state("networkidle")

    # Read placeholder directly from the visible input on the apply page
    date_box = page.locator(".oxd-date-input input").first
    date_box.wait_for(state="visible", timeout=10000)
    raw_ph = (date_box.get_attribute("placeholder") or "yyyy-mm-dd").lower()
    date_fmt = raw_ph.replace("yyyy", "%Y").replace("dd", "%d").replace("mm", "%m")

    target = future_workday(14, year=State.target_year)
    State.leave_date = target.strftime(date_fmt)

    apply_leave(page, State.leave_date)

    # Verify submission success or no field errors
    try:
        expect(page.locator(".oxd-toast")).to_contain_text("Success", timeout=10000)
    except Exception:
        errs = page.locator(".oxd-input-field-error-message").all_inner_texts()
        if errs:
            shot(page, "err_apply_leave_validation")
            raise AssertionError(f"Apply leave failed with validation errors: {errs}")
    shot(page, "02_applied")


def test_step_07_verify_request_in_my_leave(emp_page):
    filter_my_leave(emp_page)
    expect(emp_page.locator(".oxd-table-card", has_text=State.leave_date).first).to_be_visible(timeout=15000)


def test_step_08_and_09_verify_status_pending(emp_page):
    filter_my_leave(emp_page, State.leave_date)
    row = emp_page.locator(".oxd-table-card", has_text=State.leave_date)
    expect(row).to_have_count(1)
    expect(row).to_contain_text("Pending Approval")
    shot(emp_page, "03_status")


def test_step_10_and_11_duplicate_rejection(emp_page):
    page = emp_page
    apply_leave(page, State.leave_date)
    expect(
        page.locator(".oxd-toast--error, .oxd-text--danger, .oxd-dialog-container-default, :text('Overlapping'), .oxd-input-field-error-message").first
    ).to_be_visible(timeout=15000)
    shot(page, "04_overlap_error")

    ok = page.get_by_role("button", name="Ok")
    if ok.is_visible():
        ok.click()

    filter_my_leave(page, State.leave_date)
    expect(page.locator(".oxd-table-card", has_text=State.leave_date)).to_have_count(1)