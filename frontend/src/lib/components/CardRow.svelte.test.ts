import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import CardRow from './CardRow.svelte';

describe('CardRow', () => {
	it('creates its zoom state on first render without mutating reactive state', () => {
		const screen = render(CardRow, { kind: 'table', cardIds: ['1.jpg', '2.jpg'] });

		expect(screen.container.querySelectorAll('.slot')).toHaveLength(2);
	});
});
