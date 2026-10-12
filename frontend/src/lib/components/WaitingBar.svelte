<script lang="ts">
	let { message }: { message: string | null } = $props();
</script>

{#if message}
	<div class="spacer" aria-hidden="true"></div>
	<div class="waiting-bar" role="status" aria-live="polite">
		<span class="pulse" aria-hidden="true"></span>
		{#key message}
			<span class="text">{message}</span>
		{/key}
	</div>
{/if}

<style>
	/* Keeps the last bit of the page from ending up hidden behind the bar. */
	.spacer {
		height: calc(var(--tap) + var(--space-6));
	}

	/* A floating, slightly see-through pill rather than a full-width strip: it
	 * stays out of the way of content on wide screens, and the blur keeps text
	 * legible when cards scroll underneath it. */
	.waiting-bar {
		position: fixed;
		bottom: var(--space-4);
		left: 50%;
		z-index: 30;
		display: flex;
		align-items: center;
		gap: var(--space-3);
		max-width: calc(100vw - 2 * var(--space-4));
		padding: var(--space-3) var(--space-4);
		border: var(--border-width) solid var(--color-border);
		border-radius: 999px;
		background: color-mix(in srgb, var(--color-surface) 88%, transparent);
		backdrop-filter: blur(10px);
		-webkit-backdrop-filter: blur(10px);
		box-shadow: var(--shadow-overlay);
		color: var(--color-text);
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		transform: translateX(-50%);
		animation: bar-in 0.2s ease-out;
	}

	.pulse {
		flex-shrink: 0;
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--color-accent);
		animation: pulse 1.6s ease-in-out infinite;
	}

	.text {
		animation: text-in 0.2s ease-out;
	}

	@keyframes bar-in {
		from {
			opacity: 0;
			transform: translate(-50%, 8px);
		}
		to {
			opacity: 1;
			transform: translate(-50%, 0);
		}
	}

	@keyframes text-in {
		from {
			opacity: 0;
		}
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.4;
			transform: scale(0.8);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.waiting-bar,
		.text,
		.pulse {
			animation: none;
		}
	}
</style>
