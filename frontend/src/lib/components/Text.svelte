<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variant = 'title' | 'heading' | 'body' | 'caption' | 'label' | 'tag' | 'button-label';
	type Tag = 'h1' | 'h2' | 'p' | 'span' | 'label' | 'div';

	const DEFAULT_TAG: Record<Variant, Tag> = {
		title: 'h1',
		heading: 'h2',
		body: 'p',
		caption: 'p',
		label: 'span',
		tag: 'span',
		'button-label': 'span'
	};

	interface Props {
		variant: Variant;
		as?: Tag;
		for?: string;
		class?: string;
		children: Snippet;
	}

	let { variant, as, for: htmlFor, class: className = '', children }: Props = $props();
	let tag = $derived(as ?? DEFAULT_TAG[variant]);
</script>

<svelte:element this={tag} class="text text--{variant} {className}" for={htmlFor}>
	{@render children()}
</svelte:element>

<style>
	.text {
		margin: 0;
	}

	/* title/heading otherwise add nothing beyond the tag itself: the global
	 * h1/h2/h3 rule in app.css already pins family/weight/size for every
	 * heading in the app, so an <h1>/<h2> here inherits it for free.
	 */

	.text--title {
		/* Only "title" (the single Dixit wordmark) needs this: it's the one
		 * heading that gets vertically centered against unrelated sibling
		 * content instead of sitting in its own block, so its line box's
		 * font-metric ascent/descent padding (invisible slack a plain center
		 * alignment can't distinguish from real content) would otherwise throw
		 * that centering off - trimming it to the glyphs' own edges fixes that
		 * regardless of which font actually renders.
		 */
		text-box-trim: trim-both;
		text-box-edge: cap alphabetic;
	}

	.text--body {
		font-family: var(--font-sans);
		font-size: var(--size-md);
		font-weight: var(--weight-normal);
		color: var(--color-text);
		line-height: 1.5;
	}

	.text--caption {
		font-family: var(--font-sans);
		font-size: var(--size-md);
		font-weight: var(--weight-normal);
		color: var(--color-text-quiet);
		line-height: 1.5;
	}

	.text--label {
		font-family: var(--font-sans);
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		color: var(--color-text-quiet);
		line-height: 1.2;
	}

	.text--tag {
		font-family: var(--font-sans);
		font-size: var(--size-xs);
		font-weight: var(--weight-normal);
		color: var(--color-text-quiet);
		line-height: 1.2;
	}

	.text--button-label {
		font-family: var(--font-sans);
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		color: inherit;
		line-height: 1;
	}
</style>
