<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();
</script>

<div class="panel-header">
	{@render children()}
</div>

<style>
	.panel-header {
		display: flex;
		flex-wrap: wrap;
		/* Bottom-, not center-, aligned: the zoom control's own box is taller
		 * than the heading text (a generous touch target on its slider), so
		 * center-aligning would leave the heading sitting above the row's true
		 * bottom edge - invisible slack that margin-bottom below can't see,
		 * making the visible gap bigger here than on a heading with no zoom
		 * control next to it. Bottom-aligning keeps the heading's own edge (and
		 * so the visible gap after it) the same everywhere, control or not. */
		align-items: flex-end;
		justify-content: space-between;
		gap: var(--space-2) var(--space-3);
		/* The one gap between any panel's heading and whatever it introduces
		 * (a card row, a stat table, ...), so it reads the same everywhere
		 * instead of depending on that first element's own, unrelated margin. */
		margin-bottom: var(--space-6);
	}
</style>
