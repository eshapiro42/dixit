<script lang="ts">
	import Text from './Text.svelte';

	interface Props {
		host: string;
		prompt: string;
	}

	let { host, prompt }: Props = $props();
</script>

<figure class="prompt">
	<Text as="figcaption" variant="tag">{host}'s prompt</Text>
	<blockquote>&ldquo;{prompt}&rdquo;</blockquote>
</figure>

<style>
	.prompt {
		margin: 0 0 var(--space-4);
	}

	blockquote {
		margin: 0;
		font-size: var(--size-lg);
		font-weight: var(--weight-medium);
		overflow-wrap: anywhere;
	}
</style>
