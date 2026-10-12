<script lang="ts">
	let { message }: { message: string | null } = $props();
</script>

<!-- The live region stays mounted so a new message is announced when it changes. -->
<div class="sr-only" role="status">{message ?? ''}</div>

{#if message}
	<!-- Pushed to the bottom of a full-height page, then sticky once the page scrolls. -->
	<div class="dock">
		<div class="waiting-bar">
			<span class="pulse" aria-hidden="true"></span>
			{#key message}
				<span class="text">{message}</span>
			{/key}
		</div>
	</div>
{/if}

<style>
	.dock {
		position: sticky;
		bottom: max(var(--space-4), env(safe-area-inset-bottom));
		z-index: var(--z-pill);
		display: flex;
		justify-content: center;
		margin-top: auto;
		padding-top: var(--space-4);
		pointer-events: none;
	}

	.waiting-bar {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		max-width: 100%;
		padding: var(--space-3) var(--space-4);
		border: var(--border-width) solid var(--color-border-strong);
		border-radius: var(--radius);
		background: color-mix(in srgb, var(--color-surface-raised) 88%, transparent);
		backdrop-filter: blur(10px);
		-webkit-backdrop-filter: blur(10px);
		box-shadow: var(--shadow-overlay);
		color: var(--color-text);
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		pointer-events: auto;
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
			transform: translateY(8px);
		}
	}

	@keyframes text-in {
		from {
			opacity: 0;
		}
	}

	@keyframes pulse {
		50% {
			opacity: 0.4;
			transform: scale(0.8);
		}
	}
</style>
