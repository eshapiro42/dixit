import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ScoreBoard from './ScoreBoard.svelte';

function names(container: Element): string[] {
	return [...container.querySelectorAll('.player-name')].map((el) => el.textContent ?? '');
}

describe('ScoreBoard', () => {
	it('ranks players by score, highest first', () => {
		const screen = render(ScoreBoard, {
			players: [
				{ name: 'alice', score: 4, is_cpu: false },
				{ name: 'bob', score: 9, is_cpu: false }
			]
		});

		expect(names(screen.container)).toEqual(['bob', 'alice']);
		const ranks = [...screen.container.querySelectorAll('.rank')].map((el) => el.textContent);
		expect(ranks).toEqual(['1', '2']);
	});

	it('lists cpu players after the humans, without a rank', () => {
		const screen = render(ScoreBoard, {
			players: [
				{ name: 'CPU 1', score: 0, is_cpu: true },
				{ name: 'alice', score: 0, is_cpu: false }
			]
		});

		expect(names(screen.container)).toEqual(['alice', 'CPU 1']);
		const ranks = [...screen.container.querySelectorAll('.rank')].map((el) => el.textContent);
		expect(ranks).toEqual(['1', '']);
	});

	it('marks the current host as storyteller', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'alice', score: 0, is_cpu: false }],
			hostName: 'alice'
		});

		expect(screen.container.textContent).toContain('Storyteller');
	});

	it('gives each player a full-name tooltip so a truncated name stays readable', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'Bartholomew-Maximilian-Fitz', score: 1, is_cpu: false }]
		});

		expect(screen.container.querySelector('.player-name')?.getAttribute('title')).toBe(
			'Bartholomew-Maximilian-Fitz'
		);
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
			players: [{ name: 'CPU 1', score: 0, is_cpu: true }],
			deltas: { 'CPU 1': 0 }
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
