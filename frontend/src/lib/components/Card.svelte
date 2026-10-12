<script lang="ts">
	import { api } from '../api/client';
	import Badge from './Badge.svelte';
	import CardPreview from './CardPreview.svelte';
	import Text from './Text.svelte';

	interface Props {
		cardId: string;
		selected?: boolean;
		dimmed?: boolean;
		selectable?: boolean;
		onselect?: () => void;
		label?: string;
		votes?: string[];
		delta?: number;
		accessibleLabel?: string;
	}

	let {
		cardId,
		selected = false,
		dimmed = false,
		selectable = false,
		onselect,
		label,
		votes,
		delta,
		accessibleLabel
	}: Props = $props();

	// Long enough that sweeping the mouse across a row of cards doesn't flash
	// previews, short enough to feel responsive to someone who actually wants one.
	const PREVIEW_DELAY_MS = 600;

	let previewAnchor = $state<DOMRect | null>(null);

	function hoverPreview(node: HTMLElement) {
		let timer: ReturnType<typeof setTimeout> | undefined;

		function hide(): void {
			clearTimeout(timer);
			previewAnchor = null;
		}

		function onEnter(event: PointerEvent): void {
			if (event.pointerType !== 'mouse') return;
			clearTimeout(timer);
			timer = setTimeout(() => (previewAnchor = node.getBoundingClientRect()), PREVIEW_DELAY_MS);
		}

		function onKeydown(event: KeyboardEvent): void {
			if (event.key === 'Escape') hide();
		}

		node.addEventListener('pointerenter', onEnter);
		node.addEventListener('pointerleave', hide);
		node.addEventListener('pointerdown', hide);
		// Capture: the carousel scrolls inside its own container, and scroll
		// events don't bubble.
		window.addEventListener('scroll', hide, true);
		window.addEventListener('keydown', onKeydown);

		return {
			destroy() {
				hide();
				node.removeEventListener('pointerenter', onEnter);
				node.removeEventListener('pointerleave', hide);
				node.removeEventListener('pointerdown', hide);
				window.removeEventListener('scroll', hide, true);
				window.removeEventListener('keydown', onKeydown);
			}
		};
	}
</script>

<div class="card-wrap">
	{#if label}<Text as="span" variant="tag" class="card-name">{label}</Text>{/if}
	<div class="frame" use:hoverPreview>
		{#if selectable}
			<button
				type="button"
				class="card"
				class:selected
				class:dimmed
				onclick={onselect}
				aria-pressed={selected}
				aria-label={accessibleLabel ?? label ?? 'Card'}
			>
				<img src={api.cardImageUrl(cardId)} alt="" loading="lazy" />
			</button>
		{:else}
			<div class="card" class:selected class:dimmed>
				<img src={api.cardImageUrl(cardId)} alt="" loading="lazy" />
			</div>
		{/if}
		{#if previewAnchor}
			<CardPreview {cardId} anchor={previewAnchor} />
		{/if}
		{#if selected}
			<Badge tone="solid" shape="circle" class="check" ariaHidden>&check;</Badge>
		{/if}
		{#if delta !== undefined}
			<Badge tone="solid" size="delta" class="delta" ariaHidden>+{delta}</Badge>
		{/if}
	</div>
	{#each votes ?? [] as voter (voter)}
		<Text as="span" variant="tag" class="card-caption">{voter}'s vote</Text>
	{/each}
</div>

<style>
	.frame {
		position: relative;
	}

	.card {
		display: block;
		width: 100%;
		aspect-ratio: 363 / 527;
		padding: 0;
		border: none;
		/* --radius-card is tuned for the card's size at minimum zoom; scale it
		 * with --zoom so the corner stays proportional to the card instead of
		 * shrinking toward a plain rectangle as the card grows. Capped so the
		 * curve can never grow past where the (fixed-distance, non-scaling)
		 * check/delta badges sit - past that point the corner's own rounding
		 * would cut into the badge instead of just the card's artwork.
		 */
		border-radius: min(
			calc(var(--radius-card) * var(--zoom, var(--zoom-min, 0.6)) / var(--zoom-min, 0.6)),
			20px
		);
		overflow: hidden;
		background: var(--color-surface);
		/* The selected-state ring lives in its own layer (transparent unless
		 * .selected) so it composes with whichever ambient shadow is active
		 * instead of the two fighting over the box-shadow property. It's an
		 * INSET ring rather than an outline: an outline would render outside
		 * the card's own box, which a carousel with its cards flush against
		 * the scrollport edge (for exact alignment with sibling elements) has
		 * no room to show without either clipping it or jumping the layout to
		 * make room only when selected.
		 */
		--ring: inset 0 0 0 0 transparent;
		box-shadow: var(--ring), var(--shadow-card);
		cursor: default;
		transition:
			transform 0.15s ease,
			box-shadow 0.15s ease,
			opacity 0.15s ease;
	}

	button.card {
		cursor: pointer;
	}

	button.card:hover {
		transform: translateY(-4px);
		box-shadow: var(--ring), var(--shadow-card-hover);
	}

	button.card:active {
		transform: scale(0.97);
	}

	.card.selected {
		--ring: inset 0 0 0 var(--accent-line) var(--color-accent);
	}

	/* A modifier-key click (Shift/Ctrl/Cmd) is treated by browsers as a
	 * focus-visible-worthy interaction, so it was painting the platform's
	 * raw default outline - reuse the same inset ring the selected state
	 * already uses instead of suppressing focus styling altogether. */
	button.card:focus-visible {
		outline: none;
		--ring: inset 0 0 0 var(--accent-line) var(--color-accent);
	}

	.card.dimmed {
		opacity: 0.55;
	}

	/* Lets a player glance at any other card at full strength without having
	 * to select it first - the dim is just a resting state, not a lock. */
	button.card.dimmed:hover {
		opacity: 1;
	}

	img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.frame :global(.check),
	.frame :global(.delta) {
		position: absolute;
		top: var(--space-2);
		pointer-events: none;
	}

	.frame :global(.check) {
		right: var(--space-2);
		width: 24px;
		height: 24px;
		font-size: var(--size-sm);
		transform: translateY(0);
		transition: transform 0.15s ease;
	}

	/* The check badge is a sibling of .card, not a child of it (a child would
	 * get clipped by .card's own overflow: hidden corner rounding), so it
	 * doesn't move with .card's own hover lift for free - carry the same
	 * translate over by hand so it visibly stays attached to the card. */
	button.card:hover ~ :global(.check) {
		transform: translateY(-4px);
	}

	.frame :global(.delta) {
		left: var(--space-2);
	}

	.card-wrap :global(.card-caption) {
		display: block;
		margin-top: var(--space-1);
		text-align: center;
	}

	.card-wrap :global(.card-name) {
		display: block;
		margin-bottom: var(--space-1);
		text-align: center;
		font-weight: var(--weight-bold);
		color: var(--color-text);
	}
</style>
