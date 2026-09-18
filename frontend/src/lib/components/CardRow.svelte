<script lang="ts">
	import Card from './Card.svelte';
	import { zoomState } from '../game/zoom.svelte';

	interface Props {
		cardIds: string[];
		selectedId?: string | null;
		selectable?: boolean;
		onselect?: (cardId: string) => void;
		labels?: Record<string, string>;
		votes?: Record<string, string[]>;
	}

	let { cardIds, selectedId = null, selectable = false, onselect, labels, votes }: Props = $props();
</script>

<div class="row" role="list" style:--zoom={zoomState.value}>
	{#each cardIds as cardId, index (cardId)}
		<div class="slot" role="listitem">
			<Card
				{cardId}
				selected={cardId === selectedId}
				{selectable}
				onselect={() => onselect?.(cardId)}
				label={labels?.[cardId]}
				votes={votes?.[cardId]}
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
		padding: var(--space-2) var(--space-1) var(--space-3);
		margin-bottom: var(--space-2);
		scrollbar-width: thin;
		scrollbar-color: var(--color-border) transparent;
	}

	.row::-webkit-scrollbar {
		height: 8px;
	}

	.row::-webkit-scrollbar-track {
		background: transparent;
	}

	.row::-webkit-scrollbar-thumb {
		background: var(--color-border);
		border-radius: var(--radius);
	}

	.row::-webkit-scrollbar-thumb:hover {
		background: var(--color-text-quiet);
	}

	.slot {
		flex: 0 0 auto;
		width: calc(clamp(90px, 22vw, 150px) * var(--zoom, 1));
	}
</style>
