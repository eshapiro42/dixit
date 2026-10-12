<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		wide?: boolean;
		children: Snippet;
	}

	let { wide = false, children }: Props = $props();
</script>

<div class="shell" class:wide>
	{@render children()}
</div>

<style>
	.shell {
		max-width: 60rem;
		margin: 0 auto;
		padding: var(--space-4) var(--page-gutter);
	}

	.shell.wide {
		max-width: var(--page-max);
	}
</style>
