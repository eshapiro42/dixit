<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variant = 'title' | 'heading' | 'body' | 'caption' | 'label' | 'tag' | 'button-label';
	type Tag = 'h1' | 'h2' | 'p' | 'span' | 'label' | 'div' | 'figcaption';

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
		id?: string;
		for?: string;
		title?: string;
		class?: string;
		children: Snippet;
	}

	let { variant, as, id, for: htmlFor, title, class: className = '', children }: Props = $props();
	let tag = $derived(as ?? DEFAULT_TAG[variant]);
</script>

<svelte:element this={tag} class="text text--{variant} {className}" {id} for={htmlFor} {title}>
	{@render children()}
</svelte:element>

<style>
	.text {
		margin: 0;
	}

	/* title and heading inherit their look from the global h1/h2 rule. */

	.text--title {
		/* Trim the wordmark's line box so it centers optically in the top bar. */
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
