import { expect, test, type Page } from '@playwright/test';

const PLAYERS = [
	'alice',
	'bob',
	'carol',
	'dave',
	'Bartholomew-Maximilian-Fitz',
	'CPU 1',
	'CPU 2'
].map((name) => ({ name, score: 3, is_cpu: name.startsWith('CPU') }));

const HAND = Array.from({ length: 6 }, (_, i) => `${i + 1}.jpg`);

function view(overrides: Record<string, unknown>) {
	return {
		game_id: 'ABCD',
		creator_name: 'alice',
		started: true,
		playable: true,
		min_players: 4,
		min_human_players: 3,
		players: PLAYERS,
		phase: 'host_choosing',
		host: 'bob',
		prompt: 'a whisper in the dark that lasts forever and ever',
		table: null,
		votes_cast: 0,
		votes_needed: 3,
		player_name: 'alice',
		is_creator: true,
		hand: HAND,
		mulligan_available: true,
		has_played: false,
		has_voted: false,
		previous_round_outcome: null,
		round_outcomes: [],
		messages: [],
		...overrides
	};
}

const STATES: Record<string, Record<string, unknown>> = {
	lobby: { started: false, phase: null, host: null, playable: false },
	'waiting for the storyteller': { phase: 'host_choosing', host: 'bob' },
	'storyteller choosing': { phase: 'host_choosing', host: 'alice' },
	'choosing a card': { phase: 'others_choosing', host: 'bob' },
	voting: { phase: 'voting', host: 'bob', table: HAND }
};

async function mockSession(page: Page, session: unknown): Promise<void> {
	await page.route('**/api/session', (route) => route.fulfill({ status: 200, json: session }));
	await page.route('**/api/cards/**', (route) =>
		route.fulfill({
			status: 200,
			contentType: 'image/svg+xml',
			body: '<svg xmlns="http://www.w3.org/2000/svg" width="363" height="527"><rect width="363" height="527" fill="#888"/></svg>'
		})
	);
}

for (const [name, overrides] of Object.entries(STATES)) {
	test(`${name} never scrolls sideways on a small phone`, async ({ page }) => {
		await page.setViewportSize({ width: 360, height: 640 });
		await mockSession(page, view(overrides));

		await page.goto('/');
		await expect(page.locator('.topbar')).toBeVisible();

		const { scrollWidth, clientWidth } = await page.evaluate(() => ({
			scrollWidth: document.documentElement.scrollWidth,
			clientWidth: document.documentElement.clientWidth
		}));
		expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
	});
}

test('the top bar keeps everything on one row on a small phone', async ({ page }) => {
	await page.setViewportSize({ width: 360, height: 640 });
	await mockSession(page, view({ phase: 'others_choosing' }));

	await page.goto('/');
	await expect(page.locator('.status')).toBeVisible();

	const centers = await page.evaluate(() =>
		['.wordmark', '.status', '.actions'].map((selector) => {
			const box = document.querySelector(selector)!.getBoundingClientRect();
			return box.top + box.height / 2;
		})
	);
	for (const center of centers) expect(Math.abs(center - centers[0])).toBeLessThan(3);
});

test('the menu holds Game Log, the theme switch and Leave Game', async ({ page }) => {
	await page.setViewportSize({ width: 360, height: 640 });
	await mockSession(page, view({ phase: 'others_choosing' }));

	await page.goto('/');
	await page.getByRole('button', { name: 'Menu' }).click();

	await expect(page.getByRole('button', { name: 'Game Log', exact: true })).toBeVisible();
	await expect(page.getByRole('button', { name: /theme/i })).toBeVisible();
	await expect(page.getByRole('button', { name: 'Leave Game', exact: true })).toBeVisible();
});

for (const [name, size, overrides] of [
	[
		'a short page on desktop',
		{ width: 1280, height: 800 },
		{ phase: 'host_choosing', host: 'bob' }
	],
	[
		'a long page on a phone',
		{ width: 360, height: 640 },
		{ phase: 'others_choosing', host: 'alice' }
	]
] as const) {
	test(`the waiting message sits at the bottom of the screen on ${name}`, async ({ page }) => {
		await page.setViewportSize(size);
		await mockSession(page, view(overrides));

		await page.goto('/');
		const pill = page.locator('.waiting-bar');
		await expect(pill).toBeVisible();

		const gap = await pill.evaluate((el) => innerHeight - el.getBoundingClientRect().bottom);
		expect(gap).toBeGreaterThanOrEqual(8);
		expect(gap).toBeLessThanOrEqual(24);
	});
}
