<script lang="ts">
	import Card from './Card.svelte';

	interface Props {
		cardIds: string[];
		selectedId?: string | null;
		selectable?: boolean;
		onselect?: (cardId: string) => void;
		labels?: Record<string, string>;
	}

	let { cardIds, selectedId = null, selectable = false, onselect, labels }: Props = $props();
</script>

<div class="row" role="list">
	{#each cardIds as cardId, index (cardId)}
		<div class="slot" role="listitem">
			<Card
				{cardId}
				selected={cardId === selectedId}
				{selectable}
				onselect={() => onselect?.(cardId)}
				label={labels?.[cardId]}
				accessibleLabel={labels?.[cardId] ?? `Card ${index + 1} of ${cardIds.length}`}
			/>
		</div>
	{/each}
</div>

<style>
	.row {
		display: flex;
		gap: var(--space-3);
		overflow-x: auto;
		padding: var(--space-2) var(--space-1) var(--space-4);
	}

	.slot {
		flex: 0 0 auto;
		width: clamp(90px, 22vw, 150px);
	}
</style>
