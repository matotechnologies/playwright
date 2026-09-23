const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  use: {
    baseURL: 'http://localhost:4200',
    headless: true,
  },
  reporter: [['html', { outputFolder: 'playwright-report', open: 'never' }]],
});
