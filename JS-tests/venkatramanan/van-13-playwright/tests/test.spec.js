/**
 * OrangeHRM end-to-end leave test (JavaScript + Playwright Test) - default port 4201
 *
 * Flow:
 *   SETUP (Admin)  : create new employee with login -> ensure leave type -> add entitlement
 *   TEST (Employee): the 11 steps
 */
const base = require('@playwright/test');
const fs = require('fs');

const test = base.test;
const expect = base.expect.configure({ timeout: 15000 });

const BASE = process.env.OHRM_URL || 'http://localhost:4201';
const ADMIN_USER = process.env.OHRM_ADMIN_USER || 'Admin';
const ADMIN_PASS = process.env.OHRM_ADMIN_PASS || 'admin123';
const LEAVE_TYPE = process.env.OHRM_LEAVE_TYPE || 'Casual Leave';
const ENTITLEMENT = process.env.OHRM_ENTITLEMENT || '10';
const REASON = 'Family function - automation test';

const SUF = String(Date.now()).slice(-6); // unique per run
const FIRST = 'Auto';
const LAST = `Emp${SUF}`;
const EMP_USER = `auto${SUF}`;
const EMP_PASS = 'Xk9#mPq2$vLw'; // strong password (avoids "guessable" hint)

fs.mkdirSync('screenshots', { recursive: true });

function futureWorkday(days = 14) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1);
  return d;
}
const target = futureWorkday();

const shot = (page, name) => page.screenshot({ path: `screenshots/${name}.png` });

const field = (page, label) =>
  page.locator('.oxd-input-group')
    .filter({ has: page.locator(`label:text-is("${label}")`) })
    .locator('input');

async function login(page, user, pwd) {
  await page.goto(`${BASE}/web/index.php/auth/login`);
  await page.getByPlaceholder('Username').fill(user);
  await page.getByPlaceholder('Password').fill(pwd);
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page).toHaveURL(/dashboard/);
}

// ---------------------------------------------------------------- ADMIN SETUP
async function createEmployee(page) {
  const apiLog = [];
  page.on('response', async (r) => {
    const m = r.request().method();
    if (r.url().includes('/api/v2/') && (m === 'POST' || m === 'PUT')) {
      let body = '';
      try { body = (await r.text()).slice(0, 300); } catch (e) { /* ignore */ }
      apiLog.push(`${m} ${r.url().split('/api/v2/')[1]} -> ${r.status()} ${body}`);
    }
  });

  await page.goto(`${BASE}/web/index.php/pim/addEmployee`);
  await page.getByPlaceholder('First Name').fill(FIRST);
  await page.getByPlaceholder('Last Name').fill(LAST);
  await page.locator('.oxd-switch-input').click(); // Create Login Details
  await field(page, 'Username').fill(EMP_USER);
  await field(page, 'Password').fill(EMP_PASS);
  await field(page, 'Confirm Password').fill(EMP_PASS);
  await page.keyboard.press('Tab');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2500); // username uniqueness API

  for (const attempt of [1, 2]) {
    const save = page.getByRole('button', { name: 'Save' });
    console.log(`   Save try ${attempt}: disabled=${await save.isDisabled()}`);
    await save.click();
    try {
      await page.waitForURL(/viewPersonalDetails/, { timeout: 10000 });
      return;
    } catch (e) {
      await shot(page, `err_add_employee_try${attempt}`);
      console.log('   Field messages:', await page.locator('.oxd-input-field-error-message').allInnerTexts());
      console.log('   API calls so far:');
      apiLog.forEach((l) => console.log('     ', l));
      await page.waitForTimeout(2000);
    }
  }
  throw new Error('Employee was not created - see screenshots/err_add_employee_try*.png');
}

// ---------------------------------------------------------------- HELPERS (employee)
async function detectDate(page) {
  await page.goto(`${BASE}/web/index.php/leave/applyLeave`);
  await page.locator('.oxd-select-text').first().click();
  await page.getByRole('option', { name: LEAVE_TYPE, exact: true }).click();
  const ph = (await page.locator('.oxd-date-input input').first().getAttribute('placeholder')) || 'yyyy-dd-mm';
  const yyyy = String(target.getFullYear());
  const dd = String(target.getDate()).padStart(2, '0');
  const mm = String(target.getMonth() + 1).padStart(2, '0');
  return ph.replace('yyyy', yyyy).replace('dd', dd).replace('mm', mm);
}

async function setDates(page, d) {
  for (const i of [0, 1]) {
    const box = page.locator('.oxd-date-input input').nth(i);
    await box.click();
    await box.press('Control+a');
    await box.fill(d);
    await box.press('Tab'); // close calendar popup
  }
  await page.locator('h5, h6').first().click(); // neutral click
  await page.waitForTimeout(500);
}

async function applyLeave(page, d) {
  await page.goto(`${BASE}/web/index.php/leave/applyLeave`);
  await page.locator('.oxd-select-text').first().click();
  await page.getByRole('option', { name: LEAVE_TYPE, exact: true }).click();
  await setDates(page, d);
  await page.locator('textarea').fill(REASON);
  await page.getByRole('button', { name: 'Apply' }).click();
}

async function filterMyLeave(page, d, status = 'Pending Approval') {
  await page.goto(`${BASE}/web/index.php/leave/viewMyLeaveList`);
  await page.locator('.oxd-select-text').nth(0).click();
  await page.getByRole('option', { name: status }).click();
  if (d) await setDates(page, d);
  await page.getByRole('button', { name: 'Search' }).click();
  await page.waitForTimeout(1000);
}

// ---------------------------------------------------------------- TESTS
test.describe.serial('OrangeHRM - Setup + Employee leave flow', () => {
  test.setTimeout(180000);
  let adminPage, empPage, leaveDate;

  test.beforeAll(async ({ browser }) => {
    console.log('Running against:', BASE);
    adminPage = await (await browser.newContext()).newPage(); // separate sessions
    empPage = await (await browser.newContext()).newPage();
  });

  test.afterAll(async () => {
    await adminPage.context().close();
    await empPage.context().close();
  });

  // ------------------------------------------------------------ ADMIN SETUP
  test('SETUP-1 Admin login + create employee with login details', async () => {
    await login(adminPage, ADMIN_USER, ADMIN_PASS);
    console.log(`   Creating employee ${FIRST} ${LAST} (user: ${EMP_USER})`);
    await createEmployee(adminPage);
  });

  test('SETUP-2 Ensure leave type exists', async () => {
    const page = adminPage;
    await page.goto(`${BASE}/web/index.php/leave/leaveTypeList`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    if ((await page.locator('.oxd-table-card', { hasText: LEAVE_TYPE }).count()) === 0) {
      console.log('   Leave type not found, creating...');
      await page.goto(`${BASE}/web/index.php/leave/defineLeaveType`);
      await field(page, 'Name').fill(LEAVE_TYPE);
      await page.getByRole('button', { name: 'Save' }).click();
      await page.waitForURL(/leaveTypeList/, { timeout: 15000 });
    } else {
      console.log('   Leave type already exists, skipping');
    }
  });

  test('SETUP-3 Add entitlement for the new employee', async () => {
    const page = adminPage;
    await page.goto(`${BASE}/web/index.php/leave/addLeaveEntitlement`);
    await page.getByPlaceholder('Type for hints...').fill(`${FIRST} ${LAST}`);
    await page.locator('.oxd-autocomplete-option', { hasText: LAST }).first().click();
    await page.locator('.oxd-select-text').nth(0).click();
    await page.getByRole('option', { name: LEAVE_TYPE, exact: true }).click();
    await page.locator('.oxd-select-text').nth(1).click();
    await page.getByRole('option', { name: new RegExp(`^${target.getFullYear()}-`) }).click();
    await field(page, 'Entitlement').fill(ENTITLEMENT);
    await page.getByRole('button', { name: 'Save' }).click();
    await page.getByRole('button', { name: 'Confirm' }).click({ timeout: 5000 }).catch(() => {});
    await page.waitForURL(/viewLeaveEntitlements/, { timeout: 15000 });
    await shot(page, '00_admin_entitlement');
  });

  // ------------------------------------------------------------ EMPLOYEE FLOW
  test('1. Login as employee', async () => {
    await login(empPage, EMP_USER, EMP_PASS);
  });

  test('2. Check available leave balance', async () => {
    await empPage.goto(`${BASE}/web/index.php/leave/viewLeaveModule`);
    await empPage.locator('.oxd-topbar-body-nav-tab', { hasText: 'Entitlements' }).click();
    await empPage.getByText('My Entitlements', { exact: true }).click();
    await empPage.waitForLoadState('networkidle');
    await expect(empPage.locator('.oxd-table-body')).toBeVisible();
    const body = (await empPage.locator('.oxd-table-body').innerText()).replace(/\n/g, ' | ');
    console.log('   Entitlements:', body);
    expect(body).toContain(LEAVE_TYPE);
    expect(body).toContain(ENTITLEMENT);
    await shot(empPage, '01_balance');
  });

  test('3-6. Apply leave (future date, type, reason) and submit', async () => {
    leaveDate = await detectDate(empPage);
    console.log('   Leave date:', leaveDate);
    await applyLeave(empPage, leaveDate);
    await expect(empPage.locator('.oxd-toast')).toContainText('Success');
    await shot(empPage, '02_applied');
  });

  test('7. Request appears in My Leave', async () => {
    await filterMyLeave(empPage);
    await expect(empPage.locator('.oxd-table-card', { hasText: leaveDate }).first()).toBeVisible();
  });

  test('8-9. Filter by date + status, verify Pending Approval', async () => {
    await filterMyLeave(empPage, leaveDate, 'Pending Approval');
    const row = empPage.locator('.oxd-table-card', { hasText: leaveDate });
    await expect(row).toHaveCount(1);
    await expect(row).toContainText('Pending Approval');
    await shot(empPage, '03_status');
  });

  test('10-11. Duplicate request for same date is rejected', async () => {
    await applyLeave(empPage, leaveDate);
    await expect(empPage.getByText('Overlapping Leave Request', { exact: false })).toBeVisible();
    await shot(empPage, '04_overlap_error');

    const ok = empPage.getByRole('button', { name: 'Ok' });
    if (await ok.isVisible()) await ok.click();

    await filterMyLeave(empPage, leaveDate, 'Pending Approval');
    await expect(empPage.locator('.oxd-table-card', { hasText: leaveDate })).toHaveCount(1);
  });
});