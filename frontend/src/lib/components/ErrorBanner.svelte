<script lang="ts">
	import IconButton from './IconButton.svelte';
	import Text from './Text.svelte';

	interface Props {
		message: string | null;
		ondismiss?: () => void;
	}

	let { message, ondismiss }: Props = $props();
</script>

{#if message}
	<div class="banner" role="alert">
		<Text as="span" variant="body" class="banner-message">{message}</Text>
		<IconButton label="Dismiss" tone="danger" onclick={() => ondismiss?.()} />
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
	}

	/* Text's "body" variant sets its own color; override back to the banner's
	 * danger red, which the plain dismiss icon still inherits from .banner.
	 */
	.banner :global(.banner-message) {
		color: inherit;
	}
</style>
