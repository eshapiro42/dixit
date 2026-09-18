<script lang="ts">
	import type { RoundOutcome } from '../../api/types';
	import CardRow from '../CardRow.svelte';

	let { outcome }: { outcome: RoundOutcome } = $props();

	let cardIds = $derived(Object.values(outcome.table));
	let labels = $derived(
		Object.fromEntries(Object.entries(outcome.table).map(([name, cardId]) => [cardId, name]))
	);
	let votes = $derived.by(() => {
		const byCard: Record<string, string[]> = {};
		for (const [voter, cardId] of Object.entries(outcome.votes)) {
			(byCard[cardId] ??= []).push(voter);
		}
		return byCard;
	});
</script>

<section class="outcome">
	<h2>Table</h2>
	<p class="quiet">{outcome.host}'s prompt: "{outcome.prompt}"</p>
	<CardRow {cardIds} {labels} {votes} />
</section>

<style>
	.outcome {
		border-top: 1px solid var(--color-border);
		margin-top: var(--space-4);
		padding-top: var(--space-4);
	}
</style>
