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
		deltas?: Record<string, number>;
	}

	let {
		cardIds,
		selectedId = null,
		selectable = false,
		onselect,
		labels,
		votes,
		deltas
	}: Props = $props();
</script>

<div class="row" role="list" style:--zoom={zoomState.value}>
	{#each cardIds as cardId, index (cardId)}
		<div class="slot" role="listitem">
			<Card
				{cardId}
				selected={cardId === selectedId}
				dimmed={selectable && selectedId !== null && cardId !== selectedId}
				{selectable}
				onselect={() => onselect?.(cardId)}
				label={labels?.[cardId]}
				votes={votes?.[cardId]}
				delta={deltas?.[cardId]}
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
		padding: var(--space-2) var(--space-3) var(--space-3);
		margin-bottom: var(--space-2);
		scroll-snap-type: x proximity;
		/* Padding alone only insets the very first/last card; scroll-padding
		 * keeps that same breathing room around whichever card is snapped to,
		 * so a mid-scroll card's shadow doesn't get clipped against the edge.
		 */
		scroll-padding-inline: var(--space-3);
		/* Deliberately no scrollbar-width/scrollbar-color here: setting either
		 * to a non-default value makes Chrome 121+ ignore every
		 * ::-webkit-scrollbar-* rule below, which is the only way to control
		 * the arrow buttons specifically.
		 */
	}

	.row::-webkit-scrollbar {
		height: 8px;
	}

	.row::-webkit-scrollbar-button {
		display: none;
		width: 0;
		height: 0;
	}

	.row::-webkit-scrollbar-track {
		background: transparent;
	}

	.row::-webkit-scrollbar-thumb {
		background: var(--color-accent);
		border-radius: var(--radius);
	}

	.row::-webkit-scrollbar-thumb:hover {
		filter: brightness(0.9);
	}

	.slot {
		flex: 0 0 auto;
		width: calc(clamp(90px, 22vw, 150px) * var(--zoom, 1));
		scroll-snap-align: start;
	}
</style>
