import { afterEach, describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { SessionView } from '../../api/types';
import { gameState } from '../../game/state.svelte';
import GameLobby from './GameLobby.svelte';

function lobbyView(overrides: Partial<SessionView> = {}): SessionView {
	return {
		game_id: 'ABCD',
		creator_name: 'alice',
		started: false,
		playable: false,
		min_players: 4,
		min_human_players: 3,
		players: [
			{ name: 'alice', score: 0, is_cpu: false },
			{ name: 'bob', score: 0, is_cpu: false },
			{ name: 'CPU 1', score: 0, is_cpu: true }
		],
		phase: null,
		host: null,
		prompt: null,
		table: null,
		votes_cast: 0,
		votes_needed: 0,
		player_name: 'alice',
		is_creator: true,
		hand: [],
		mulligan_available: false,
		has_played: false,
		has_voted: false,
		previous_round_outcome: null,
		round_outcomes: [],
		messages: [],
		...overrides
	};
}

describe('GameLobby', () => {
	afterEach(() => vi.restoreAllMocks());

	it('lets the creator remove other players and CPUs, but not themselves', async () => {
		const remove = vi.spyOn(gameState, 'removePlayer').mockResolvedValue();
		const screen = render(GameLobby, { view: lobbyView() });

		await expect
			.element(screen.getByRole('button', { name: 'Remove alice' }))
			.not.toBeInTheDocument();
		await screen.getByRole('button', { name: 'Remove bob' }).click();
		await screen.getByRole('button', { name: 'Remove CPU 1' }).click();

		expect(remove).toHaveBeenNthCalledWith(1, 'bob');
		expect(remove).toHaveBeenNthCalledWith(2, 'CPU 1');
	});

	it('gives other players no remove buttons', () => {
		const screen = render(GameLobby, {
			view: lobbyView({ player_name: 'bob', is_creator: false })
		});

		expect(screen.container.querySelectorAll('button[aria-label^="Remove"]')).toHaveLength(0);
	});

	it('says what is still needed to start, and drops the hint once the game can start', async () => {
		const screen = render(GameLobby, { view: lobbyView() });
		expect(screen.container.textContent).toContain('Invite 1 more person to start.');

		await screen.rerender({
			view: lobbyView({
				playable: true,
				players: [
					{ name: 'alice', score: 0, is_cpu: false },
					{ name: 'bob', score: 0, is_cpu: false },
					{ name: 'carol', score: 0, is_cpu: false },
					{ name: 'CPU 1', score: 0, is_cpu: true }
				]
			})
		});

		expect(screen.container.textContent).not.toContain('to start.');
	});
});
