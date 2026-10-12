<script lang="ts">
	import Card from './Card.svelte';
	import { getZoomState, ZOOM_MIN, type ZoomKind } from '../game/zoom.svelte';

	interface Props {
		kind: ZoomKind;
		cardIds: string[];
		selectedId?: string | null;
		selectable?: boolean;
		onselect?: (cardId: string) => void;
		labels?: Record<string, string>;
		votes?: Record<string, string[]>;
		deltas?: Record<string, number>;
	}

	let {
		kind,
		cardIds,
		selectedId = null,
		selectable = false,
		onselect,
		labels,
		votes,
		deltas
	}: Props = $props();

	let zoom = $derived(getZoomState(kind));
</script>

<div
	class="row"
	role="list"
	data-zoom-kind={kind}
	style:--zoom={zoom.value}
	style:--zoom-min={ZOOM_MIN}
>
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
		overscroll-behavior-x: contain;
		/* No horizontal padding: the inset selection ring never overflows a card. */
		padding: var(--space-3) 0;
		margin: var(--space-4) 0;
		scroll-snap-type: x proximity;
		/* Setting scrollbar-width or scrollbar-color makes Chrome ignore the ::-webkit-scrollbar rules below. */
	}

	.row::-webkit-scrollbar {
		height: var(--accent-line);
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
		width: calc(clamp(90px, min(38vw, 32vh), 150px) * var(--zoom, 1));
		scroll-snap-align: start;
	}
</style>
