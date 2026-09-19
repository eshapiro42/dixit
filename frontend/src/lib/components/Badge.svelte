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
		/* line-height alone still centers the font's full ascent/descent box,
		 * not the actual glyph ink - for a font whose ascent and descent aren't
		 * symmetric around its cap height (most of them), that leaves the text
		 * looking off-center within an otherwise-centered box, and which way it
		 * leans is font-specific. Trimming the box to the glyph's own edges
		 * makes flex centering land on the ink itself instead. No-op in
		 * browsers that don't support it yet - falls back to the line-height
		 * behavior above.
		 */
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

	/* The score-delta "+N" badge specifically: one shared size so the version
	 * on the storyteller's card and the version next to a score in the table
	 * are pixel-identical, not two independently-tuned lookalikes. */
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
