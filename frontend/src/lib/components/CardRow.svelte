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
		/* Chrome 121+ ignores ::-webkit-scrollbar-* entirely once scrollbar-width
		 * or scrollbar-color is set to anything but its default, and the standard
		 * properties have no way to hide just the arrow buttons — so there's no
		 * way to keep a styled bar without them. Hide the scrollbar outright
		 * instead; the scroll-snapped, partially cut-off cards already show
		 * there's more to scroll to.
		 */
		scrollbar-width: none;
	}

	.row::-webkit-scrollbar {
		display: none;
	}

	.slot {
		flex: 0 0 auto;
		width: calc(clamp(90px, 22vw, 150px) * var(--zoom, 1));
		scroll-snap-align: start;
	}
</style>
