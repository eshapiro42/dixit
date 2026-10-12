<script lang="ts">
	import { api } from '../api/client';

	interface Props {
		cardId: string;
		anchor: DOMRect;
	}

	let { cardId, anchor }: Props = $props();

	const ASPECT = 363 / 527;
	const MARGIN = 16;
	const GAP = 12;
	const MAX_HEIGHT = 640;

	let box = $derived.by(() => {
		const viewportWidth = window.innerWidth;
		const viewportHeight = window.innerHeight;

		let height = Math.min(MAX_HEIGHT, viewportHeight - 2 * MARGIN);
		let width = height * ASPECT;
		if (width > viewportWidth - 2 * MARGIN) {
			width = viewportWidth - 2 * MARGIN;
			height = width / ASPECT;
		}

		const roomRight = viewportWidth - MARGIN - (anchor.right + GAP);
		const roomLeft = anchor.left - GAP - MARGIN;
		let left: number;
		if (roomRight >= width) left = anchor.right + GAP;
		else if (roomLeft >= width) left = anchor.left - GAP - width;
		else left = (viewportWidth - width) / 2;

		const centered = anchor.top + anchor.height / 2 - height / 2;
		const top = Math.max(MARGIN, Math.min(centered, viewportHeight - MARGIN - height));

		return { left, top, width, height };
	});
</script>

<div
	class="preview"
	style:left="{box.left}px"
	style:top="{box.top}px"
	style:width="{box.width}px"
	style:height="{box.height}px"
	aria-hidden="true"
>
	<img src={api.cardImageUrl(cardId)} alt="" />
</div>

<style>
	.preview {
		position: fixed;
		z-index: 40;
		pointer-events: none;
		border-radius: 16px;
		overflow: hidden;
		background: var(--color-surface);
		box-shadow: var(--shadow-overlay);
		animation: preview-in 0.14s ease-out;
	}

	.preview img {
		display: block;
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	@keyframes preview-in {
		from {
			opacity: 0;
			transform: scale(0.96);
		}
		to {
			opacity: 1;
			transform: scale(1);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.preview {
			animation: none;
		}
	}
</style>
