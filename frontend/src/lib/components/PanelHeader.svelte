<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		/** Baseline suits plain text; the default end suits a taller control beside the heading. */
		align?: 'end' | 'baseline';
		children: Snippet;
	}

	let { align = 'end', children }: Props = $props();
</script>

<div class="panel-header {align}">
	{@render children()}
</div>

<style>
	.panel-header {
		display: flex;
		flex-wrap: wrap;
		/* Bottom-aligned so the gap below the heading is the same with or without a zoom control. */
		align-items: flex-end;
		justify-content: space-between;
		gap: var(--space-2) var(--space-3);
		/* The single gap between a heading and whatever follows it. */
		margin-bottom: var(--space-6);
	}

	.baseline {
		align-items: baseline;
	}
</style>
