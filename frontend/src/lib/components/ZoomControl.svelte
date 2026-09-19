<script lang="ts">
	import { getZoomState, ZOOM_MIN, ZOOM_MAX, type ZoomKind } from '../game/zoom.svelte';
	import Text from './Text.svelte';

	interface Props {
		kind: ZoomKind;
	}

	let { kind }: Props = $props();
	let zoom = $derived(getZoomState(kind));

	const zoomId = $props.id();

	// Sizes this specific carousel's row so its cards exactly fill the
	// available width - no leftover space, no horizontal scrollbar - by
	// reading the row's actual layout (padding, gap, current card width)
	// rather than duplicating CardRow's own sizing formula here. Scoped to
	// this control's own kind since more than one carousel (e.g. the hand and
	// a round's results) can be on screen, each with its own zoom, at once.
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

<div class="zoom-control">
	<Text as="label" variant="label" for={zoomId} class="zoom-label">Zoom</Text>
	<input
		id={zoomId}
		type="range"
		min={ZOOM_MIN}
		max={ZOOM_MAX}
		step="any"
		bind:value={zoom.value}
		ondblclick={fitToViewport}
	/>
</div>

<style>
	.zoom-control {
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}

	/* Text's shared "label" variant sizes its line box from font-relative
	 * line-height, which (like the badge text elsewhere) can sit optically
	 * off-center from a geometrically-centered sibling depending on which
	 * font a browser substitutes in. Scoped locally rather than changed on
	 * the shared variant itself, which many other unrelated layouts also
	 * depend on for their own spacing.
	 */
	.zoom-control :global(.zoom-label) {
		text-box-trim: trim-both;
		text-box-edge: cap alphabetic;
	}

	/* Fully custom track/thumb instead of the platform's native range-input
	 * chrome: the native rendering is what was producing the blue
	 * drag-highlight and the gray track border neither of which is
	 * something CSS here ever asked for - it's just each OS/browser's
	 * default. Matches the card carousel's scrollbar (--accent-line
	 * thickness, transparent-ish flat track, solid accent handle) instead
	 * of inventing a second, different-looking slider style.
	 */
	.zoom-control input[type='range'] {
		-webkit-appearance: none;
		appearance: none;
		width: 100px;
		height: var(--tap);
		background: transparent;
		margin: 0;
		cursor: pointer;
	}

	.zoom-control input[type='range']:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: 2px;
	}

	.zoom-control input[type='range']::-webkit-slider-runnable-track {
		height: var(--accent-line);
		background: var(--color-border);
		border-radius: var(--radius);
	}

	.zoom-control input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		width: 10px;
		height: 10px;
		margin-top: calc((var(--accent-line) - 10px) / 2);
		border-radius: 50%;
		background: var(--color-accent);
		border: none;
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
		width: 10px;
		height: 10px;
		border-radius: 50%;
		background: var(--color-accent);
		border: none;
		cursor: pointer;
	}

	.zoom-control input[type='range']::-moz-range-thumb:hover {
		filter: brightness(0.9);
	}
</style>
