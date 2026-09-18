import { expect, test } from '@playwright/test';

const SESSION_VIEW = {
	game_id: 'ABCD',
	creator_name: 'alice',
	started: false,
	playable: false,
	min_players: 4,
	min_human_players: 3,
	players: [{ name: 'alice', score: 0, is_cpu: false }],
	phase: null,
	host: null,
	prompt: null,
	table: null,
	votes_cast: 0,
	votes_needed: 0,
	player_name: 'alice',
	is_creator: true,
	hand: ['1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.jpg'],
	mulligan_available: false,
	has_played: false,
	has_voted: false,
	previous_round_outcome: null,
	messages: []
};

test('creating a game shows the in-game lobby without changing the URL', async ({ page }) => {
	await page.route('**/api/session', (route) =>
		route.fulfill({ status: 401, json: { error: 'no session' } })
	);
	await page.route('**/api/games', (route) => route.fulfill({ status: 200, json: SESSION_VIEW }));

	await page.goto('/');
	await page.getByLabel('Your Name').fill('alice');
	await page.getByRole('button', { name: "Let's Move It" }).click();

	await expect(page.getByText('Game ID: ABCD')).toBeVisible();
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
	await page.getByRole('tab', { name: 'Join a Game' }).click();
	await page.getByLabel('Game ID').fill('NOPE');
	await page.getByLabel('Your Name').fill('alice');
	await page.getByRole('button', { name: "Let's Groove It" }).click();

	const banner = page.getByRole('alert');
	await expect(banner).toContainText('Game NOPE was not found.');
	await banner.getByRole('button', { name: 'Dismiss' }).click();
	await expect(banner).not.toBeVisible();
});
