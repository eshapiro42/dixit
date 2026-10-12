<script lang="ts">
	import { bunnyMaskUrl } from '../bunny';
	import IconButton from './IconButton.svelte';
	import { getZoomState, ZOOM_MIN, ZOOM_MAX, type ZoomKind } from '../game/zoom.svelte';

	interface Props {
		kind: ZoomKind;
	}

	let { kind }: Props = $props();
	let zoom = $derived(getZoomState(kind));

	const zoomId = $props.id();

	// Fits this kind's row to the available width, reading its real layout.
	function fitToViewport(): void {
		const row = document.querySelector<HTMLElement>(`.row[data-zoom-kind="${kind}"]`);
		if (!row) return;
		const cards = row.querySelectorAll<HTMLElement>('.slot');
		if (cards.length === 0) return;

		const currentCardWidth = cards[0].getBoundingClientRect().width;
		if (currentCardWidth <= 0) return;
		const baseCardWidth = currentCardWidth / zoom.value;

		const style = getComputedStyle(row);
		const gap = parseFloat(style.columnGap) || 0;
		const usableWidth =
			row.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);

		const neededCardWidth = (usableWidth - (cards.length - 1) * gap) / cards.length;
		const neededZoom = neededCardWidth / baseCardWidth;

		zoom.value = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, neededZoom));
	}
</script>

<div class="zoom-control" style:--bunny-mask={bunnyMaskUrl()}>
	<input
		id={zoomId}
		type="range"
		min={ZOOM_MIN}
		max={ZOOM_MAX}
		step="any"
		bind:value={zoom.value}
		aria-label="Card size"
		aria-valuetext="{Math.round(zoom.value * 100)}%"
		ondblclick={fitToViewport}
	/>
	<IconButton icon="fit" label="Fit cards to screen" onclick={fitToViewport} />
</div>

<style>
	.zoom-control {
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}

	/* Custom track and thumb to match the card carousel's scrollbar. */
	.zoom-control input[type='range'] {
		-webkit-appearance: none;
		appearance: none;
		width: 100px;
		height: var(--tap);
		background: transparent;
		margin: 0;
		cursor: pointer;
	}

	.zoom-control input[type='range']::-webkit-slider-runnable-track {
		height: var(--accent-line);
		background: var(--color-border);
		border-radius: var(--radius);
	}

	/* The thumb is the bunny: a mask lets it take the accent color. */
	.zoom-control input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		width: 14px;
		height: 24px;
		margin-top: calc((var(--accent-line) - 24px) / 2);
		border: none;
		background: var(--color-accent);
		-webkit-mask: var(--bunny-mask) center / contain no-repeat;
		mask: var(--bunny-mask) center / contain no-repeat;
		cursor: pointer;
	}

	.zoom-control input[type='range']::-webkit-slider-thumb:hover {
		filter: brightness(0.9);
	}

	.zoom-control input[type='range']::-moz-range-track {
		height: var(--accent-line);
		background: var(--color-border);
		border-radius: var(--radius);
	}

	.zoom-control input[type='range']::-moz-range-thumb {
		width: 14px;
		height: 24px;
		border: none;
		border-radius: 0;
		background: var(--color-accent);
		mask: var(--bunny-mask) center / contain no-repeat;
		cursor: pointer;
	}

	.zoom-control input[type='range']::-moz-range-thumb:hover {
		filter: brightness(0.9);
	}
</style>
