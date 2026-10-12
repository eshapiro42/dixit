import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ScoreBoard from './ScoreBoard.svelte';

describe('ScoreBoard', () => {
	it('ranks players by score, highest first, as a two-row grid', () => {
		const screen = render(ScoreBoard, {
			players: [
				{ name: 'alice', score: 4, is_cpu: false },
				{ name: 'bob', score: 9, is_cpu: false }
			]
		});
		const names = screen.container.querySelectorAll('[role="columnheader"]');
		const scores = screen.container.querySelectorAll('[role="cell"]');
		expect(names[0].textContent).toContain('bob');
		expect(names[1].textContent).toContain('alice');
		expect(scores[0].textContent?.trim()).toBe('9');
		expect(scores[1].textContent?.trim()).toBe('4');
	});

	it('marks the current host as storyteller', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'alice', score: 0, is_cpu: false }],
			hostName: 'alice'
		});
		expect(screen.container.textContent).toContain('Storyteller');
	});

	it('does not call out cpu players separately', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'CPU-1', score: 0, is_cpu: true }]
		});
		expect(screen.container.textContent).not.toContain('CPU-1 ·');
	});

	it('shows a delta badge for a human player with a recorded delta', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'alice', score: 5, is_cpu: false }],
			deltas: { alice: 3 }
		});
		expect(screen.container.querySelector('.delta')?.textContent).toBe('+3');
	});

	it('omits the delta badge for cpu players even when a delta is recorded', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'CPU-1', score: 0, is_cpu: true }],
			deltas: { 'CPU-1': 0 }
		});
		expect(screen.container.querySelector('.delta')).toBeNull();
	});

	it('omits the delta badge when no deltas are given at all', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'alice', score: 5, is_cpu: false }]
		});
		expect(screen.container.querySelector('.delta')).toBeNull();
	});
});
