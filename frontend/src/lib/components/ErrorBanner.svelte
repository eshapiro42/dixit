<script lang="ts">
	interface Props {
		message: string | null;
		ondismiss?: () => void;
	}

	let { message, ondismiss }: Props = $props();
</script>

{#if message}
	<div class="banner" role="alert">
		<span>{message}</span>
		<button type="button" aria-label="Dismiss" onclick={ondismiss}>&times;</button>
	</div>
{/if}

<style>
	.banner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-3);
		padding: var(--space-3) var(--space-4);
		border-radius: var(--radius);
		background: var(--color-danger-soft);
		color: var(--color-danger);
		font-size: var(--size-sm);
	}

	button {
		background: none;
		border: none;
		color: inherit;
		font-size: var(--size-lg);
		line-height: 1;
		cursor: pointer;
		padding: 0 var(--space-1);
	}
</style>
