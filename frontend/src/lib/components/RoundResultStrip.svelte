<script lang="ts">
	import type { RoundOutcome } from '../api/types';
	import Card from './Card.svelte';

	let { outcome }: { outcome: RoundOutcome } = $props();

	let entries = $derived(Object.entries(outcome.table));
</script>

<ul class="strip" aria-label="Round {outcome.round_number} cards">
	{#each entries as [name, cardId] (cardId)}
		<li class="thumb">
			<Card {cardId} label={name} accessibleLabel="{name}'s card" />
		</li>
	{/each}
</ul>

<style>
	.strip {
		display: flex;
		gap: var(--space-2);
		margin: 0;
		padding: var(--space-1) 0 var(--space-2);
		list-style: none;
		overflow-x: auto;
	}

	.thumb {
		flex: 0 0 auto;
		width: 56px;
	}

	/* Clip long names so every thumbnail keeps the same height. */
	.thumb :global(.card-name) {
		overflow: hidden;
		white-space: nowrap;
		text-overflow: ellipsis;
		font-size: var(--size-xs);
	}
</style>
