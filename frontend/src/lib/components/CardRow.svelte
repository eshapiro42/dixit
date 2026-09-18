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
		--row-bg: var(--color-surface);
		display: flex;
		gap: var(--space-3);
		overflow-x: auto;
		padding: var(--space-2) var(--space-1) var(--space-3);
		margin-bottom: var(--space-2);
		scrollbar-width: thin;
		scrollbar-color: var(--color-border) transparent;
		scroll-snap-type: x proximity;
		/* Edge-fade scroll cue: the outer two gradients (background-attachment:
		 * scroll) only show once there's actually more to scroll to, since the
		 * inner two (attachment: local) scroll with the content and cover them
		 * at either end.
		 */
		background:
			linear-gradient(to right, var(--row-bg) 30%, transparent),
			linear-gradient(to left, var(--row-bg) 30%, transparent) 100% 0,
			linear-gradient(to right, rgb(32 28 43 / 0.12), transparent),
			linear-gradient(to left, rgb(32 28 43 / 0.12), transparent) 100% 0;
		background-repeat: no-repeat;
		background-color: var(--row-bg);
		background-size:
			32px 100%,
			32px 100%,
			12px 100%,
			12px 100%;
		background-attachment: local, local, scroll, scroll;
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
		scroll-snap-align: start;
	}
</style>
