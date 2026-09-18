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
		max-width: 960px;
		margin: 0 auto;
		padding: var(--space-4);
	}

	.shell.wide {
		max-width: 1400px;
	}

	@media (max-width: 480px) {
		.shell {
			padding: var(--space-2);
		}
	}
</style>
