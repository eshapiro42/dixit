import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: './e2e',
	testMatch: '**/*.e2e.{ts,js}',
	webServer: { command: 'npm run build && npm run preview', port: 4173 },
	use: { baseURL: 'http://127.0.0.1:4173' }
});
