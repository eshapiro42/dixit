import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Card from './Card.svelte';

describe('Card', () => {
	it('gives a selectable card an accessible name', () => {
		const screen = render(Card, {
			cardId: '1.jpg',
			selectable: true,
			accessibleLabel: 'Card 2 of 6'
		});
		const button = screen.container.querySelector('button');
		expect(button?.getAttribute('aria-label')).toBe('Card 2 of 6');
	});

	it('falls back to a generic name when nothing more specific is given', () => {
		const screen = render(Card, { cardId: '1.jpg', selectable: true });
		const button = screen.container.querySelector('button');
		expect(button?.getAttribute('aria-label')).toBe('Card');
	});

	it('does not render a button at all when not selectable', () => {
		const screen = render(Card, { cardId: '1.jpg' });
		expect(screen.container.querySelector('button')).toBeNull();
	});
});
