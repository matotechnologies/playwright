import os
import re
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect

BASE = os.getenv("OHRM_URL", "http://localhost:4201")
ADMIN_USER = os.getenv("OHRM_ADMIN_USER", "Admin")
ADMIN_PASS = os.getenv("OHRM_ADMIN_PASS", "admin123")
LEAVE_TYPE = os.getenv("OHRM_LEAVE_TYPE", "Casual Leave")
ENTITLEMENT = os.getenv("OHRM_ENTITLEMENT", "10")
HEADLESS = os.getenv("HEADLESS", "0") == "1"
REASON = "Family function - automation test"

SUF = str(int(time.time()))[-6:]  # unique per run
FIRST, LAST = "Auto", f"Emp{SUF}"
EMP_USER, EMP_PASS = f"auto{SUF}", "Xk9#mPq2$vLw"

expect.set_options(timeout=15000)
os.makedirs("screenshots", exist_ok=True)


def step(tag, msg):
    print(f"[{tag:>6}] {msg}")


def shot(page, name):
    page.screenshot(path=f"screenshots/{name}.png")


def future_workday(days=14):
    d = date.today() + timedelta(days=days)
    while d.weekday() >= 5:  # skip Sat/Sun
        d += timedelta(days=1)
    return d


def field(page, label):
    return (
        page.locator(".oxd-input-group")
        .filter(has=page.locator(f'label:text-is("{label}")'))
        .locator("input")
    )


def login(page, user, pwd):
    page.goto(f"{BASE}/web/index.php/auth/login")
    page.get_by_placeholder("Username").fill(user)
    page.get_by_placeholder("Password").fill(pwd)
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile("dashboard"))


# ---------------------------------------------------------------- ADMIN SETUP
def create_employee(page):
    api_log = []

    def on_resp(r):
        if "/api/v2/" in r.url and r.request.method in ("POST", "PUT"):
            try:
                body = r.text()[:300]
            except Exception:
                body = ""
            api_log.append(f"{r.request.method} {r.url.split('/api/v2/')[1]} -> {r.status} {body}")

    page.on("response", on_resp)

    page.goto(f"{BASE}/web/index.php/pim/addEmployee")
    page.get_by_placeholder("First Name").fill(FIRST)
    page.get_by_placeholder("Last Name").fill(LAST)
    page.locator(".oxd-switch-input").click()  # Create Login Details
    field(page, "Username").fill(EMP_USER)
    field(page, "Password").fill(EMP_PASS)
    field(page, "Confirm Password").fill(EMP_PASS)
    page.keyboard.press("Tab")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2500)

    for attempt in (1, 2):
        save = page.get_by_role("button", name="Save")
        print(f"   Save try {attempt}: disabled={save.is_disabled()}")
        save.click()
        try:
            page.wait_for_url(re.compile("viewPersonalDetails"), timeout=10000)
            return
        except Exception:
            shot(page, f"err_add_employee_try{attempt}")
            print("   Field messages:", page.locator(".oxd-input-field-error-message").all_inner_texts())
            print("   API calls so far:")
            for line in api_log:
                print("     ", line)
            page.wait_for_timeout(2000)
    raise AssertionError("Employee was not created - see screenshots/err_add_employee_try*.png")


def admin_setup(page, year):
    step("SETUP", f"Admin login ({BASE})")
    login(page, ADMIN_USER, ADMIN_PASS)

    step("SETUP", f"Create employee {FIRST} {LAST} (user: {EMP_USER})")
    create_employee(page)

    step("SETUP", f"Ensure leave type '{LEAVE_TYPE}' exists")
    page.goto(f"{BASE}/web/index.php/leave/leaveTypeList")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)  # wait for list to render
    if page.locator(".oxd-table-card", has_text=LEAVE_TYPE).count() == 0:
        print("   Leave type not found, creating...")
        page.goto(f"{BASE}/web/index.php/leave/defineLeaveType")
        field(page, "Name").fill(LEAVE_TYPE)
        page.get_by_role("button", name="Save").click()
        page.wait_for_url(re.compile("leaveTypeList"), timeout=15000)
    else:
        print("   Leave type already exists, skipping")

    step("SETUP", f"Add {ENTITLEMENT} days entitlement for {year}")
    page.goto(f"{BASE}/web/index.php/leave/addLeaveEntitlement")
    page.get_by_placeholder("Type for hints...").fill(f"{FIRST} {LAST}")
    page.locator(".oxd-autocomplete-option", has_text=LAST).first.click()
    page.locator(".oxd-select-text").nth(0).click()
    page.get_by_role("option", name=LEAVE_TYPE, exact=True).click()
    page.locator(".oxd-select-text").nth(1).click()
    page.get_by_role("option", name=re.compile(rf"^{year}-")).click()
    field(page, "Entitlement").fill(ENTITLEMENT)
    page.get_by_role("button", name="Save").click()
    try:
        page.get_by_role("button", name="Confirm").click(timeout=5000)  # update dialog
    except Exception:
        pass
    page.wait_for_url(re.compile("viewLeaveEntitlements"), timeout=15000)
    shot(page, "00_admin_entitlement")


# ---------------------------------------------------------------- EMPLOYEE FLOW
def detect_date_fmt(page):
    """Read the date placeholder (e.g. yyyy-dd-mm) and convert to strftime format."""
    page.goto(f"{BASE}/web/index.php/leave/applyLeave")
    page.locator(".oxd-select-text").first.click()
    page.get_by_role("option", name=LEAVE_TYPE, exact=True).click()
    ph = page.locator(".oxd-date-input input").first.get_attribute("placeholder") or "yyyy-dd-mm"
    return ph.replace("yyyy", "%Y").replace("dd", "%d").replace("mm", "%m")


def set_dates(page, d):
    for i in (0, 1):
        box = page.locator(".oxd-date-input input").nth(i)
        box.click()
        box.press("Control+a")
        box.fill(d)
        box.press("Tab")
    page.locator("h5, h6").first.click()  # neutral click to dismiss calendar
    page.wait_for_timeout(500)


def apply_leave(page, d):
    page.goto(f"{BASE}/web/index.php/leave/applyLeave")
    page.locator(".oxd-select-text").first.click()
    page.get_by_role("option", name=LEAVE_TYPE, exact=True).click()
    set_dates(page, d)
    page.locator("textarea").fill(REASON)
    page.get_by_role("button", name="Apply").click()


def filter_my_leave(page, d=None, status="Pending Approval"):
    page.goto(f"{BASE}/web/index.php/leave/viewMyLeaveList")
    page.locator(".oxd-select-text").nth(0).click()
    page.get_by_role("option", name=status).click()
    if d:
        set_dates(page, d)
    page.get_by_role("button", name="Search").click()
    page.wait_for_timeout(1000)


def employee_flow(page, date_obj):
    step(1, f"Login as employee ({EMP_USER})")
    login(page, EMP_USER, EMP_PASS)

    step(2, "Check leave balance")
    page.goto(f"{BASE}/web/index.php/leave/viewLeaveModule")
    page.locator(".oxd-topbar-body-nav-tab", has_text="Entitlements").click()
    page.get_by_text("My Entitlements", exact=True).click()
    page.wait_for_load_state("networkidle")
    expect(page.locator(".oxd-table-body")).to_be_visible()
    body = page.locator(".oxd-table-body").inner_text().replace("\n", " | ")
    print("         Entitlements:", body)
    assert LEAVE_TYPE in body and ENTITLEMENT in body, "Balance not as expected"
    shot(page, "01_balance")

    d = date_obj.strftime(detect_date_fmt(page))
    step(3, f"Apply leave for future date {d}")
    step(4, f"Select leave type: {LEAVE_TYPE}")
    step(5, f"Reason: {REASON}")
    step(6, "Submit request")
    apply_leave(page, d)
    expect(page.locator(".oxd-toast")).to_contain_text("Success")
    shot(page, "02_applied")

    step(7, "Verify request appears in My Leave")
    filter_my_leave(page)
    expect(page.locator(".oxd-table-card", has_text=d).first).to_be_visible()

    step(8, "Search/filter by date + status")
    filter_my_leave(page, d, "Pending Approval")
    row = page.locator(".oxd-table-card", has_text=d)
    expect(row).to_have_count(1)

    step(9, "Verify status = Pending Approval")
    expect(row).to_contain_text("Pending Approval")
    shot(page, "03_status")

    step(10, "Submit another request for the same date")
    apply_leave(page, d)

    step(11, "Verify duplicate/overlap is rejected")
    expect(page.get_by_text("Overlapping Leave Request", exact=False)).to_be_visible()
    shot(page, "04_overlap_error")
    ok = page.get_by_role("button", name="Ok")
    if ok.is_visible():
        ok.click()
    filter_my_leave(page, d, "Pending Approval")
    expect(page.locator(".oxd-table-card", has_text=d)).to_have_count(1)  # still only one row


def main():
    print("Running against:", BASE)
    target = future_workday()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=0 if HEADLESS else 200)
        admin_page = browser.new_context().new_page()  # separate sessions
        emp_page = browser.new_context().new_page()

        admin_setup(admin_page, target.year)
        employee_flow(emp_page, target)

        print("\nALL SETUP + 11 STEPS PASSED")
        browser.close()


if __name__ == "__main__":
    main()