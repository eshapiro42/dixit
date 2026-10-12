<script lang="ts">
	import type { Snippet } from 'svelte';
	import Text from './Text.svelte';

	interface Props {
		primary: Snippet;
		secondary?: Snippet;
		/** Shown while the primary action isn't available yet, to say why. */
		hint?: string | null;
	}

	let { primary, secondary, hint = null }: Props = $props();
</script>

<div class="action-bar">
	<div class="buttons">
		{@render primary()}
		{#if secondary}{@render secondary()}{/if}
	</div>
	{#if hint}
		<Text as="p" variant="caption">{hint}</Text>
	{/if}
</div>

<style>
	.action-bar {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.buttons {
		display: flex;
		gap: var(--space-3);
	}

	.buttons > :global(:first-child) {
		flex: 1 1 0;
	}

	@media (min-width: 40rem) {
		.buttons > :global(:first-child) {
			flex: 0 0 auto;
		}

		.buttons > :global(:nth-child(2)) {
			margin-inline-start: auto;
		}
	}
</style>
