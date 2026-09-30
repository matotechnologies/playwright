import os
import re
import time
import pytest
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect

LOGIN_URL = os.getenv(
    "OHRM_LOGIN_URL", "http://localhost:4201/web/index.php/auth/login")
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


def shot(page, name):
    page.screenshot(path=f"screenshots/{name}.png")


def future_workday(days=14):
    d = date.today() + timedelta(days=days)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def field(page, label):
    return (
        page.locator(".oxd-input-group")
        .filter(has=page.locator(f'label:text-is("{label}")'))
        .locator("input")
    )


def wait_for_server(page, url, retries=15, delay=4):
    print(f"\n[INIT] Connecting to {url}...")
    for i in range(retries):
        try:
            resp = page.goto(url, timeout=10000)
            if resp and resp.status < 400:
                print(
                    f"[INIT] Server reachable on attempt {i+1} (Status {resp.status})")
                return True
        except Exception as e:
            print(
                f"[INIT] Attempt {i+1}/{retries} waiting: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    return False


def login(page, user, pwd):
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    page.get_by_placeholder("Username").wait_for(
        state="visible", timeout=20000)
    page.get_by_placeholder("Username").fill(user)
    page.get_by_placeholder("Password").fill(pwd)
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile("dashboard"), timeout=20000)


def detect_date_fmt(page):
    page.goto(f"{BASE_URL}/web/index.php/leave/applyLeave")
    page.locator(".oxd-select-text").first.click()
    page.get_by_role("option", name=LEAVE_TYPE, exact=True).click()
    ph = page.locator(
        ".oxd-date-input input").first.get_attribute("placeholder") or "yyyy-dd-mm"
    return ph.replace("yyyy", "%Y").replace("dd", "%d").replace("mm", "%m")


def set_dates(page, d):
    for i in (0, 1):
        box = page.locator(".oxd-date-input input").nth(i)
        box.click()
        box.press("Control+a")
        box.fill(d)
        box.press("Tab")
    page.locator("h5, h6").first.click()
    page.wait_for_timeout(500)


def apply_leave(page, d):
    page.goto(f"{BASE_URL}/web/index.php/leave/applyLeave")
    page.locator(".oxd-select-text").first.click()
    page.get_by_role("option", name=LEAVE_TYPE, exact=True).click()
    set_dates(page, d)
    page.locator("textarea").fill(REASON)
    page.get_by_role("button", name="Apply").click()


def filter_my_leave(page, d=None, status="Pending Approval"):
    page.goto(f"{BASE_URL}/web/index.php/leave/viewMyLeaveList")
    page.locator(".oxd-select-text").nth(0).click()
    page.get_by_role("option", name=status).click()
    if d:
        set_dates(page, d)
    page.get_by_role("button", name="Search").click()
    page.wait_for_timeout(1000)


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


@pytest.fixture(scope="session")
def target_date():
    return future_workday()


class SessionState:
    formatted_date = ""


def test_setup_01_admin_login(admin_page):
    is_ready = wait_for_server(admin_page, LOGIN_URL)
    if not is_ready:
        pytest.fail(
            f"Could not connect to {LOGIN_URL}. Container might be down or not ready.")
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
    page.wait_for_timeout(2500)

    for attempt in (1, 2):
        save = page.get_by_role("button", name="Save")
        save.click()
        try:
            page.wait_for_url(re.compile("viewPersonalDetails"), timeout=15000)
            return
        except Exception:
            shot(page, f"err_add_employee_try{attempt}")
            page.wait_for_timeout(2000)
    raise AssertionError("Employee was not created - see screenshots")


def test_setup_03_ensure_leave_type(admin_page):
    page = admin_page
    page.goto(f"{BASE_URL}/web/index.php/leave/defineLeaveType")
    page.wait_for_load_state("networkidle")
    name_input = field(page, "Name")
    name_input.fill(LEAVE_TYPE)
    page.get_by_role("button", name="Save").click()
    try:
        page.wait_for_url(re.compile("leaveTypeList"), timeout=5000)
        print(f"   Created leave type: {LEAVE_TYPE}")
    except Exception:
        err = page.locator(".oxd-input-field-error-message")
        if err.is_visible() and "already exists" in err.inner_text().lower():
            print(f"   Leave type '{LEAVE_TYPE}' already exists, proceeding.")
        else:
            shot(page, "err_define_leave_type")


def test_setup_04_add_entitlement(admin_page, target_date):
    """Admin assigns quota/entitlement to newly created employee."""
    page = admin_page
    page.goto(f"{BASE_URL}/web/index.php/leave/addLeaveEntitlement")
    page.wait_for_load_state("networkidle")

    # 1. Fill Employee Autocomplete
    emp_input = page.get_by_placeholder("Type for hints...")
    emp_input.fill(FIRST)
    page.wait_for_timeout(1000)  # Wait for debounce and API request
    
    # Wait for the dropdown options list and pick the matched employee
    option = page.locator(".oxd-autocomplete-option", has_text=LAST).first
    option.wait_for(state="visible", timeout=10000)
    option.click()
    page.wait_for_timeout(500)

    # 2. Select Leave Type
    leave_type_group = page.locator(".oxd-input-group").filter(
        has=page.locator('label:text-is("Leave Type")')
    )
    leave_type_group.locator(".oxd-select-text").click()
    page.wait_for_timeout(500)

    # Try selecting configured leave type, or fallback to the first available valid type
    matched_option = page.locator(".oxd-select-dropdown").locator(".oxd-select-option", has_text=LEAVE_TYPE)
    if matched_option.count() > 0:
        matched_option.first.click()
    else:
        # Fallback: pick the first non-header option from dropdown
        page.locator(".oxd-select-dropdown .oxd-select-option").nth(1).click()

    # 3. Handle Leave Period if dropdown exists and is unselected
    period_group = page.locator(".oxd-input-group").filter(
        has=page.locator('label:text-is("Leave Period")')
    )
    if period_group.count() > 0:
        period_text = period_group.locator(".oxd-select-text").inner_text()
        if "-- Select --" in period_text or not period_text.strip():
            period_group.locator(".oxd-select-text").click()
            page.wait_for_timeout(500)
            page.locator(".oxd-select-dropdown .oxd-select-option").nth(1).click()

    # 4. Fill Entitlement amount
    entitlement_input = page.locator(".oxd-input-group").filter(
        has=page.locator('label:text-is("Entitlement")')
    ).locator("input")
    entitlement_input.fill(ENTITLEMENT)

    # 5. Click Save
    save_btn = page.get_by_role("button", name="Save")
    save_btn.click()

    # 6. Handle Confirm Dialog (if updating / duplicate entitlement popup appears)
    try:
        confirm_btn = page.get_by_role("button", name="Confirm")
        confirm_btn.wait_for(state="visible", timeout=4000)
        confirm_btn.click()
    except Exception:
        pass

    # 7. Verify navigation or success toast
    try:
        page.wait_for_url(re.compile("viewLeaveEntitlements"), timeout=15000)
    except Exception:
        # Check if success toast appeared instead of full redirect
        expect(page.locator(".oxd-toast")).to_contain_text("Success")

    shot(page, "00_admin_entitlement")


def test_step_01_employee_login(emp_page):
    login(emp_page, EMP_USER, EMP_PASS)


def test_step_02_check_balance(emp_page):
    page = emp_page
    page.goto(f"{BASE_URL}/web/index.php/leave/viewLeaveModule")
    page.locator(".oxd-topbar-body-nav-tab", has_text="Entitlements").click()
    page.get_by_text("My Entitlements", exact=True).click()
    page.wait_for_load_state("networkidle")
    expect(page.locator(".oxd-table-body")).to_be_visible()
    body = page.locator(".oxd-table-body").inner_text().replace("\n", " | ")
    assert LEAVE_TYPE in body and ENTITLEMENT in body, f"Expected {LEAVE_TYPE} with {ENTITLEMENT} days"
    shot(page, "01_balance")


def test_step_03_to_06_apply_leave(emp_page, target_date):
    page = emp_page
    SessionState.formatted_date = target_date.strftime(detect_date_fmt(page))
    apply_leave(page, SessionState.formatted_date)
    expect(page.locator(".oxd-toast")).to_contain_text("Success")
    shot(page, "02_applied")


def test_step_07_verify_request_in_my_leave(emp_page):
    filter_my_leave(emp_page)
    expect(emp_page.locator(".oxd-table-card",
           has_text=SessionState.formatted_date).first).to_be_visible()


def test_step_08_and_09_verify_status_pending(emp_page):
    filter_my_leave(emp_page, SessionState.formatted_date, "Pending Approval")
    row = emp_page.locator(
        ".oxd-table-card", has_text=SessionState.formatted_date)
    expect(row).to_have_count(1)
    expect(row).to_contain_text("Pending Approval")
    shot(emp_page, "03_status")


def test_step_10_and_11_duplicate_rejection(emp_page):
    page = emp_page
    apply_leave(page, SessionState.formatted_date)
    expect(page.get_by_text("Overlapping Leave Request", exact=False)).to_be_visible()
    shot(page, "04_overlap_error")

    ok = page.get_by_role("button", name="Ok")
    if ok.is_visible():
        ok.click()

    filter_my_leave(page, SessionState.formatted_date, "Pending Approval")
    expect(page.locator(".oxd-table-card",
           has_text=SessionState.formatted_date)).to_have_count(1)
