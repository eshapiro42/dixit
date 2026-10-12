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

	// Long enough that sweeping across a row doesn't flash previews.
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
		// Capture, since the carousel's scroll events don't bubble.
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
	{#if label}<Text as="span" variant="tag" class="card-name" title={label}>{label}</Text>{/if}
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
		position: relative;
		display: block;
		width: 100%;
		aspect-ratio: 363 / 527;
		padding: 0;
		border: none;
		/* Scales the corner with zoom, capped so it never reaches the fixed-position badges. */
		border-radius: min(
			calc(var(--radius-card) * var(--zoom, var(--zoom-min, 0.6)) / var(--zoom-min, 0.6)),
			20px
		);
		overflow: hidden;
		background: var(--color-surface);
		box-shadow: var(--shadow-card);
		cursor: default;
		transition:
			transform 0.15s ease,
			box-shadow 0.15s ease,
			opacity 0.15s ease;
	}

	/* An overlay, so the image can't paint over the ring; inset, so the carousel can't clip it. */
	.card::after {
		content: '';
		position: absolute;
		inset: 0;
		border-radius: inherit;
		box-shadow: inset 0 0 0 var(--accent-line) var(--color-accent);
		opacity: 0;
		pointer-events: none;
		transition: opacity 0.15s ease;
	}

	.card.selected::after {
		opacity: 1;
	}

	button.card {
		cursor: pointer;
	}

	button.card:focus-visible {
		outline: 2px solid var(--color-focus);
		outline-offset: -5px;
	}

	button.card:active {
		transform: scale(0.97);
	}

	@media (hover: hover) and (pointer: fine) {
		button.card:hover {
			transform: translateY(-4px);
			box-shadow: var(--shadow-card-hover);
		}

		/* The badge is a sibling of .card (overflow clips children), so mirror the hover lift. */
		button.card:hover ~ :global(.check) {
			transform: translateY(-4px);
		}

		/* A resting dim, not a lock: hover to see any card at full strength. */
		button.card.dimmed:hover {
			opacity: 1;
		}
	}

	.card.dimmed {
		opacity: 0.55;
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

	.frame :global(.delta) {
		left: var(--space-2);
	}

	/* One line each, so a long name can't push a card out of line with its neighbours. */
	.card-wrap :global(.card-name),
	.card-wrap :global(.card-caption) {
		display: block;
		overflow: hidden;
		text-align: center;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.card-wrap :global(.card-caption) {
		margin-top: var(--space-1);
	}

	.card-wrap :global(.card-name) {
		margin-bottom: var(--space-1);
		font-weight: var(--weight-bold);
		color: var(--color-text);
	}
</style>
