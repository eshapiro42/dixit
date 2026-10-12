<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		size?: 'default' | 'hero';
		children: Snippet;
	}

	let { size = 'default', children }: Props = $props();
</script>

<span class="stat stat--{size} numeric">
	{@render children()}
</span>

<style>
	.stat {
		display: inline-block;
		font-weight: var(--weight-medium);
		color: var(--color-text);
		line-height: 1;
	}

	.stat--default {
		font-family: var(--font-sans);
		font-size: var(--size-sm);
	}

	.stat--hero {
		font-family: var(--font-mono);
		font-size: var(--size-2xl);
		letter-spacing: 0.05em;
	}
</style>
