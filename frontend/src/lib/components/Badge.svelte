<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		tone?: 'solid' | 'soft';
		shape?: 'pill' | 'circle';
		size?: 'default' | 'delta';
		class?: string;
		ariaHidden?: boolean;
		children: Snippet;
	}

	let {
		tone = 'soft',
		shape = 'pill',
		size = 'default',
		class: className = '',
		ariaHidden = false,
		children
	}: Props = $props();
</script>

<span
	class="badge badge--{tone} badge--{shape} badge--{size} {className}"
	aria-hidden={ariaHidden || undefined}
>
	{@render children()}
</span>

<style>
	.badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		font-weight: var(--weight-bold);
		line-height: 1;
		/* Trim to the glyph edges so flex centering lands on the ink, not the font's line box. */
		text-box-trim: trim-both;
		text-box-edge: cap alphabetic;
	}

	.badge--pill {
		border-radius: var(--radius);
		padding: 0 var(--space-1);
	}

	.badge--circle {
		border-radius: 50%;
	}

	/* Shared size for the "+N" score delta. */
	.badge--delta {
		height: 22px;
		padding: 0 var(--space-2);
		font-size: var(--size-xs);
	}

	.badge--solid {
		background: var(--color-accent);
		color: var(--color-accent-contrast);
	}

	.badge--soft {
		background: var(--color-accent-soft);
		color: var(--color-text);
	}
</style>
