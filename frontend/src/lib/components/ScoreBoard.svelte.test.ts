import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ScoreBoard from './ScoreBoard.svelte';

describe('ScoreBoard', () => {
	it('ranks players by score, highest first', () => {
		const screen = render(ScoreBoard, {
			players: [
				{ name: 'alice', score: 4, is_cpu: false },
				{ name: 'bob', score: 9, is_cpu: false }
			]
		});
		const items = screen.container.querySelectorAll('li');
		expect(items).toHaveLength(2);
		expect(items[0].textContent).toContain('bob');
		expect(items[1].textContent).toContain('alice');
	});

	it('marks the current host with a badge', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'alice', score: 0, is_cpu: false }],
			hostName: 'alice'
		});
		expect(screen.container.querySelector('.badge')).not.toBeNull();
	});

	it('labels cpu players', () => {
		const screen = render(ScoreBoard, {
			players: [{ name: 'CPU-1', score: 0, is_cpu: true }]
		});
		expect(screen.container.textContent).toContain('CPU');
	});
});
