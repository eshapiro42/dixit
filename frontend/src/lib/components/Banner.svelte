<script lang="ts">
	import IconButton from './IconButton.svelte';
	import Text from './Text.svelte';

	interface Props {
		message: string | null;
		/** Errors interrupt screen readers; notices wait politely. */
		tone?: 'error' | 'notice';
		ondismiss?: () => void;
	}

	let { message, tone = 'error', ondismiss }: Props = $props();
</script>

{#if message}
	<div class="banner {tone}" role={tone === 'error' ? 'alert' : 'status'}>
		<Text as="span" variant="body" class="banner-message">{message}</Text>
		<IconButton
			icon="close"
			label="Dismiss"
			tone={tone === 'error' ? 'danger' : 'default'}
			onclick={() => ondismiss?.()}
		/>
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
	}

	.error {
		background: var(--color-danger-soft);
		color: var(--color-danger);
	}

	.notice {
		background: var(--color-accent-soft);
		color: var(--color-text);
	}

	/* Text's body variant sets its own color, so hand it back to the banner. */
	.banner :global(.banner-message) {
		color: inherit;
	}
</style>
