import { defineConfig } from '@playwright/test';

export default defineConfig({
    testDir: './tests',

    use: {
        baseURL: 'http://localhost:4201/web/index.php/auth/login',
        headless: true,
        screenshot: 'only-on-failure',
        trace: 'on-first-retry'
    },

    reporter: 'html'
});
