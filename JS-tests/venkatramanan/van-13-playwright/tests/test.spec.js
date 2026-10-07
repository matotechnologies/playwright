const base = require('@playwright/test');
const fs = require('fs');

const test = base.test;
const expect = base.expect.configure({ timeout: 20000 });

const BASE_URL = process.env.OHRM_LOGIN_URL || 'http://localhost:4201/web/index.php/auth/login';
const ROOT_URL = BASE_URL.split('/web/')[0];
const ADMIN_USER = process.env.OHRM_ADMIN_USER || 'Admin';
const ADMIN_PASS = process.env.OHRM_ADMIN_PASS || 'Admin@123098';
const LEAVE_TYPE = process.env.OHRM_LEAVE_TYPE || 'Casual Leave';
const ENTITLEMENT = process.env.OHRM_ENTITLEMENT || '10';
const REASON = 'Family function - automation test';

const SUF = String(Date.now()).slice(-6);
const FIRST = 'Auto';
const LAST = `Emp${SUF}`;
const EMP_USER = `auto${SUF}`;
const EMP_PASS = 'Xk9#mPq2$vLw';

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
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  await page.getByPlaceholder('Username').waitFor({ state: 'visible' });
  await page.getByPlaceholder('Username').fill(user);
  await page.getByPlaceholder('Password').fill(pwd);
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page).toHaveURL(/dashboard/);
}

async function createEmployee(page) {
  await page.goto(`${ROOT_URL}/web/index.php/pim/addEmployee`);
  await page.getByPlaceholder('First Name').fill(FIRST);
  await page.getByPlaceholder('Last Name').fill(LAST);
  await page.locator('.oxd-switch-input').click();
  await field(page, 'Username').fill(EMP_USER);
  await field(page, 'Password').fill(EMP_PASS);
  await field(page, 'Confirm Password').fill(EMP_PASS);
  await page.keyboard.press('Tab');

  // Resolved R57: wait for button state instead of waitForTimeout
  const saveBtn = page.getByRole('button', { name: 'Save' });
  await saveBtn.waitFor({ state: 'visible' });

  for (const attempt of [1, 2]) {
    await saveBtn.click();
    try {
      await page.waitForURL(/viewPersonalDetails/, { timeout: 15000 });
      return;
    } catch (e) {
      await shot(page, `err_add_employee_try${attempt}`);
      // Resolved R67: wait for button state instead of waitForTimeout
      await saveBtn.waitFor({ state: 'visible' });
    }
  }
  throw new Error('Employee was not created - see screenshots');
}

async function detectDate(page) {
  await page.goto(`${ROOT_URL}/web/index.php/leave/applyLeave`);
  await page.locator('.oxd-select-text').first().click();
  await page.locator('.oxd-select-dropdown').waitFor({ state: 'visible' });

  const opt = page.locator('.oxd-select-dropdown .oxd-select-option:not(:has-text("-- Select --"))');
  const matched = opt.filter({ hasText: LEAVE_TYPE });
  if ((await matched.count()) > 0) {
    await matched.first().click();
  } else {
    await opt.first().click();
  }

  const dateInput = page.locator('.oxd-date-input input').first();
  await dateInput.waitFor({ state: 'visible' });
  const ph = (await dateInput.getAttribute('placeholder')) || 'yyyy-dd-mm';

  const yyyy = String(target.getFullYear());
  const dd = String(target.getDate()).padStart(2, '0');
  const mm = String(target.getMonth() + 1).padStart(2, '0');
  return ph.replace('yyyy', yyyy).replace('dd', dd).replace('mm', mm);
}

async function setDates(page, d) {
  const fromBox = page.locator('.oxd-date-input input').first();
  await fromBox.waitFor({ state: 'visible' });
  const toBox = page.locator('.oxd-date-input input').last();

  for (const box of [fromBox, toBox]) {
    await box.click();
    await box.press('Control+a');
    await box.fill(d);
    await box.press('Tab');
  }

  await page.locator('h5, h6').first().click();
  // Resolved R93: wait for calendar popup overlay to close
  await page.locator('.oxd-date-input-calendar').waitFor({ state: 'detached' }).catch(() => {});
}

async function applyLeave(page, d) {
  await page.goto(`${ROOT_URL}/web/index.php/leave/applyLeave`);
  await page.locator('.oxd-select-text').first().click();
  await page.locator('.oxd-select-dropdown').waitFor({ state: 'visible' });

  const opt = page.locator('.oxd-select-dropdown .oxd-select-option:not(:has-text("-- Select --"))');
  const matched = opt.filter({ hasText: LEAVE_TYPE });
  if ((await matched.count()) > 0) {
    await matched.first().click();
  } else {
    await opt.first().click();
  }

  await setDates(page, d);
  await page.locator('textarea').fill(REASON);
  await page.getByRole('button', { name: 'Apply' }).click();
}

async function filterMyLeave(page, d, status = 'Pending Approval') {
  await page.goto(`${ROOT_URL}/web/index.php/leave/viewMyLeaveList`);
  await page.locator('.oxd-select-text').nth(0).click();
  await page.locator('.oxd-select-dropdown').waitFor({ state: 'visible' });
  await page.getByRole('option', { name: status }).click();
  if (d) await setDates(page, d);
  await page.getByRole('button', { name: 'Search' }).click();
  await page.locator('.oxd-table, .orangehrm-container').first().waitFor({ state: 'visible' });
}

test.describe.serial('OrangeHRM - Setup + Employee leave flow', () => {
  test.setTimeout(180000);
  let adminPage, empPage, leaveDate;

  test.beforeAll(async ({ browser }) => {
    adminPage = await (await browser.newContext()).newPage();
    empPage = await (await browser.newContext()).newPage();
  });

  test.afterAll(async () => {
    await adminPage.context().close();
    await empPage.context().close();
  });

  test('SETUP-1 Admin login + create employee', async () => {
    await login(adminPage, ADMIN_USER, ADMIN_PASS);
    await createEmployee(adminPage);
  });

  test('SETUP-2 Ensure leave type exists', async () => {
    const page = adminPage;

    
    await page.goto(`${ROOT_URL}/web/index.php/leave/defineLeavePeriod`);
    const savePeriodBtn = page.locator('button[type="submit"], button:has-text("Save")').first();
    if (await savePeriodBtn.isVisible()) {
      const selects = page.locator('.oxd-select-text');
      const count = await selects.count();
      for (let i = 0; i < count; i++) {
        const txt = (await selects.nth(i).innerText()).trim();
        if (txt === '' || txt.includes('-- Select --')) {
          await selects.nth(i).click();
          await page.locator('.oxd-select-dropdown .oxd-select-option:not(:has-text("-- Select --"))').first().click();
        }
      }
      await savePeriodBtn.click();
      await page.locator('.oxd-loading-spinner').waitFor({ state: 'detached' }).catch(() => {});
    }

    // 2. Check Leave Type List after data finishes loading
    await page.goto(`${ROOT_URL}/web/index.php/leave/leaveTypeList`);
    await page.locator('.oxd-loading-spinner').waitFor({ state: 'detached' }).catch(() => {});

    const exists = await page.locator('.oxd-table-card', { hasText: LEAVE_TYPE }).first().isVisible().catch(() => false);
    if (!exists) {
      const addBtn = page.getByRole('button', { name: 'Add' });
      if (await addBtn.isVisible()) {
        await addBtn.click();
        await page.getByRole('button', { name: 'Save' }).waitFor({ state: 'visible' });
        await field(page, 'Name').fill(LEAVE_TYPE);
        await page.getByRole('button', { name: 'Save' }).click();
        // Wait for redirect or error message without hanging
        await Promise.race([
          page.waitForURL(/leaveTypeList/),
          page.locator('.oxd-input-field-error-message').waitFor({ state: 'visible' })
        ]).catch(() => {});
      }
    }
  });

  test('SETUP-3 Add entitlement for new employee', async () => {
    const page = adminPage;
    await page.goto(`${ROOT_URL}/web/index.php/leave/addLeaveEntitlement`);

    
    const hint = page.getByPlaceholder('Type for hints...');
    await hint.waitFor({ state: 'visible' });
    await hint.click();
    await hint.pressSequentially(LAST, { delay: 100 });

    const empOpt = page.locator('.oxd-autocomplete-dropdown .oxd-autocomplete-option:not(:has-text("Searching"))')
      .filter({ hasText: LAST }).first();
    await empOpt.waitFor({ state: 'visible' });
    await empOpt.click();

    
    await page.locator('.oxd-select-text').nth(0).click();
    await page.locator('.oxd-select-dropdown').waitFor({ state: 'visible' });
    const ltOptions = page.locator('.oxd-select-dropdown .oxd-select-option:not(:has-text("-- Select --"))');
    const matched = ltOptions.filter({ hasText: LEAVE_TYPE });
    if ((await matched.count()) > 0) {
      await matched.first().click();
    } else {
      await ltOptions.first().click();
    }

   
    await page.locator('.oxd-select-text').nth(1).click();
    await page.locator('.oxd-select-dropdown').waitFor({ state: 'visible' });
    const periodOpt = page.locator('.oxd-select-dropdown .oxd-select-option:not(:has-text("-- Select --"))').first();
    await periodOpt.waitFor({ state: 'visible' });
    await periodOpt.click();

    await field(page, 'Entitlement').fill(ENTITLEMENT);
    await page.getByRole('button', { name: 'Save' }).click();
    await page.getByRole('button', { name: 'Confirm' }).click({ timeout: 3000 }).catch(() => {});
    await expect(page.locator('.oxd-toast').or(page.locator('.oxd-table'))).toBeVisible();
    await shot(page, '00_admin_entitlement');
  });

  test('1. Login as employee', async () => {
    await login(empPage, EMP_USER, EMP_PASS);
  });

  test('2. Check leave balance', async () => {
    await empPage.goto(`${ROOT_URL}/web/index.php/leave/viewMyLeaveEntitlements`);
    if (!(await empPage.locator('.oxd-table-body').isVisible())) {
      await empPage.goto(`${ROOT_URL}/web/index.php/leave/viewLeaveModule`);
      const entTab = empPage.locator('.oxd-topbar-body-nav-tab', { hasText: 'Entitlements' });
      if (await entTab.isVisible()) {
        await entTab.click();
        await empPage.getByText('My Entitlements', { exact: true }).click();
      }
    }
    await expect(empPage.locator('.oxd-table-body')).toBeVisible();
    const body = (await empPage.locator('.oxd-table-body').innerText()).replace(/\n/g, ' | ');
    expect(body).toContain(LEAVE_TYPE);
    expect(body).toContain(ENTITLEMENT);
    await shot(empPage, '01_balance');
  });

  test('3-6. Apply leave and submit', async () => {
    leaveDate = await detectDate(empPage);
    await applyLeave(empPage, leaveDate);
    await expect(empPage.locator('.oxd-toast')).toContainText('Success');
    await shot(empPage, '02_applied');
  });

  test('7. Verify request in My Leave', async () => {
    await filterMyLeave(empPage);
    await expect(empPage.locator('.oxd-table-card', { hasText: leaveDate }).first()).toBeVisible();
  });

  test('8-9. Filter and verify status Pending Approval', async () => {
    await filterMyLeave(empPage, leaveDate, 'Pending Approval');
    const row = empPage.locator('.oxd-table-card', { hasText: leaveDate });
    await expect(row).toHaveCount(1);
    await expect(row).toContainText('Pending Approval');
    await shot(empPage, '03_status');
  });

  test('10-11. Duplicate request rejection', async () => {
    await applyLeave(empPage, leaveDate);
    await expect(empPage.getByText('Overlapping Leave Request', { exact: false })).toBeVisible();
    await shot(empPage, '04_overlap_error');

    const ok = empPage.getByRole('button', { name: 'Ok' });
    if (await ok.isVisible()) await ok.click();

    await filterMyLeave(empPage, leaveDate, 'Pending Approval');
    await expect(empPage.locator('.oxd-table-card', { hasText: leaveDate }).toHaveCount(1);
  });
});
