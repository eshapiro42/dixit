<script lang="ts">
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div class="shell">
	{@render children()}
</div>

<style>
	.shell {
		max-width: 960px;
		margin: 0 auto;
		padding: var(--space-4);
	}
</style>
