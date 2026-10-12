import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { GameMessage, RoundOutcome } from '../api/types';
import MessageLog from './MessageLog.svelte';

function messages(count: number): GameMessage[] {
	return Array.from({ length: count }, (_, i) => ({
		text: `message ${i}`,
		emphasis: false,
		round_start: false
	}));
}

function withRounds(): GameMessage[] {
	return [
		{ text: 'alice created the game room.', emphasis: false, round_start: false },
		{ text: 'The game has started.', emphasis: true, round_start: false },
		{
			text: "It is alice's turn to choose a card and give a prompt.",
			emphasis: false,
			round_start: true
		},
		{ text: 'bob played a card.', emphasis: false, round_start: false },
		{
			text: "It is bob's turn to choose a card and give a prompt.",
			emphasis: false,
			round_start: true
		},
		{ text: 'alice played a card.', emphasis: false, round_start: false }
	];
}

describe('MessageLog', () => {
	it('always shows pre-game messages and collapses every past round but the current one', () => {
		const screen = render(MessageLog, { messages: withRounds(), open: true });
		const text = screen.container.textContent ?? '';
		expect(text).toContain('alice created the game room.');
		expect(text).toContain('Round 1');
		expect(text).toContain('Round 2');
		expect(text).not.toContain('bob played a card.');
		expect(text).toContain('alice played a card.');
	});

	it('expands a collapsed round when its toggle is clicked', async () => {
		const screen = render(MessageLog, { messages: withRounds(), open: true });

		await screen.getByRole('button', { name: /Round 1/ }).click();

		await expect.poll(() => screen.container.textContent).toContain('bob played a card.');
	});

	it("shows a finished round's prompt when collapsed and its cards once expanded", async () => {
		const outcome: RoundOutcome = {
			host: 'alice',
			round_number: 1,
			prompt: 'a quiet storm',
			table: { alice: '1.jpg', bob: '2.jpg' },
			votes: { bob: '1.jpg' },
			scores: { alice: 3, bob: 1 },
			correct_voter_count: 1
		};
		const screen = render(MessageLog, {
			messages: withRounds(),
			outcomes: [outcome],
			open: true
		});
		expect(screen.container.textContent).toContain('a quiet storm');
		expect(screen.container.querySelectorAll('.thumb')).toHaveLength(0);

		await screen.getByRole('button', { name: /Round 1/ }).click();

		await expect.poll(() => screen.container.querySelectorAll('.thumb').length).toBe(2);
	});

	it('scrolls to the bottom as new messages arrive while already at the bottom', async () => {
		const screen = render(MessageLog, { messages: messages(3), open: true });
		const log = screen.container.querySelector('.log') as HTMLElement;
		log.style.height = '40px';

		await screen.rerender({ messages: messages(20), open: true });

		expect(log.scrollTop + log.clientHeight).toBeGreaterThanOrEqual(log.scrollHeight - 1);
	});

	it('leaves the scroll position alone once the user has scrolled away from the bottom', async () => {
		const screen = render(MessageLog, { messages: messages(20), open: true });
		const log = screen.container.querySelector('.log') as HTMLElement;
		log.style.height = '40px';
		await screen.rerender({ messages: messages(20), open: true });

		log.scrollTop = 0;
		log.dispatchEvent(new Event('scroll'));

		await screen.rerender({ messages: messages(21), open: true });

		expect(log.scrollTop).toBe(0);
	});

	it('re-snaps to the bottom on reopening after messages arrived while closed', async () => {
		const screen = render(MessageLog, { messages: messages(3), open: true });
		const log = screen.container.querySelector('.log') as HTMLElement;
		log.style.height = '40px';

		// The dialog closes, history grows while it's hidden, then it reopens.
		await screen.rerender({ messages: messages(3), open: false });
		await screen.rerender({ messages: messages(20), open: false });
		await screen.rerender({ messages: messages(20), open: true });

		await expect
			.poll(() => log.scrollTop + log.clientHeight)
			.toBeGreaterThanOrEqual(log.scrollHeight - 1);
	});
});
