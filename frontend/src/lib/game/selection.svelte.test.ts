import { flushSync } from 'svelte';
import { describe, expect, it, vi } from 'vitest';
import { CardSelection } from './selection.svelte';

function setup(initial: string[], onPruned?: () => void) {
	const cards = $state({ list: initial });
	let selection!: CardSelection;
	const cleanup = $effect.root(() => {
		selection = new CardSelection(() => cards.list, onPruned);
	});
	return { cards, selection, cleanup };
}

describe('CardSelection', () => {
	it('selects a card, and deselects it when picked again', () => {
		const { selection, cleanup } = setup(['a', 'b']);

		selection.toggle('a');
		expect(selection.selectedId).toBe('a');
		selection.toggle('b');
		expect(selection.selectedId).toBe('b');
		selection.toggle('b');
		expect(selection.selectedId).toBeNull();
		cleanup();
	});

	it('drops the selection once its card leaves the row, and says so', () => {
		const onPruned = vi.fn();
		const { cards, selection, cleanup } = setup(['a', 'b'], onPruned);
		selection.toggle('a');

		cards.list = ['b', 'c'];
		flushSync();

		expect(selection.selectedId).toBeNull();
		expect(onPruned).toHaveBeenCalledOnce();
		cleanup();
	});

	it('keeps the selection while its card is still in the row', () => {
		const { cards, selection, cleanup } = setup(['a', 'b']);
		selection.toggle('a');

		cards.list = ['a', 'c'];
		flushSync();

		expect(selection.selectedId).toBe('a');
		cleanup();
	});
});
