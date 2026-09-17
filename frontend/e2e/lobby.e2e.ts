import { expect, test } from '@playwright/test';

const SESSION_VIEW = {
	game_id: 'ABCD',
	started: false,
	playable: false,
	players: [{ name: 'alice', score: 0, is_cpu: false }],
	phase: null,
	host: null,
	prompt: null,
	table: null,
	player_name: 'alice',
	is_creator: true,
	hand: ['1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.jpg'],
	mulligan_available: false,
	has_played: false,
	has_voted: false,
	previous_round_outcome: null
};

test('creating a game shows the in-game lobby without changing the URL', async ({ page }) => {
	await page.route('**/api/session', (route) =>
		route.fulfill({ status: 401, json: { error: 'no session' } })
	);
	await page.route('**/api/games', (route) => route.fulfill({ status: 200, json: SESSION_VIEW }));

	await page.goto('/');
	await page.getByLabel('Your name').fill('alice');
	await page.getByRole('button', { name: 'Create game' }).click();

	await expect(page.getByText('Game code:')).toBeVisible();
	await expect(page).toHaveURL('/');
});

test('a server error from joining is shown and dismissible', async ({ page }) => {
	await page.route('**/api/session', (route) =>
		route.fulfill({ status: 401, json: { error: 'no session' } })
	);
	await page.route('**/api/games/*/join', (route) =>
		route.fulfill({ status: 404, json: { error: 'Game NOPE was not found.' } })
	);

	await page.goto('/');
	await page.getByRole('tab', { name: 'Join a game' }).click();
	await page.getByLabel('Game code').fill('NOPE');
	await page.getByLabel('Your name').fill('alice');
	await page.getByRole('button', { name: 'Join game' }).click();

	const banner = page.getByRole('alert');
	await expect(banner).toContainText('Game NOPE was not found.');
	await banner.getByRole('button', { name: 'Dismiss' }).click();
	await expect(banner).not.toBeVisible();
});
