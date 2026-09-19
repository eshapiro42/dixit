<script lang="ts">
	import Text from './Text.svelte';

	interface Props {
		detail: string;
	}

	let { detail }: Props = $props();
</script>

<section>
	<Text variant="heading">Waiting</Text>
	<Text as="p" variant="caption">{detail}</Text>
</section>
