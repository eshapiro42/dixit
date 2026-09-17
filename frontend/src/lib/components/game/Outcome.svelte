<script lang="ts">
	import type { RoundOutcome } from '../../api/types';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';

	interface Props {
		outcome: RoundOutcome;
		ondismiss: () => void;
	}

	let { outcome, ondismiss }: Props = $props();

	let cardIds = $derived(Object.values(outcome.table));
	let labels = $derived(
		Object.fromEntries(Object.entries(outcome.table).map(([name, cardId]) => [cardId, name]))
	);
</script>

<section class="outcome">
	<h2>Last round</h2>
	<p class="quiet">{outcome.host}'s prompt: "{outcome.prompt}"</p>
	<CardRow {cardIds} {labels} />
	<Button onclick={ondismiss}>Continue</Button>
</section>

<style>
	.outcome {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-4);
		background: var(--color-accent-soft);
	}
</style>
