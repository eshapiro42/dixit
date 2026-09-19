<script lang="ts">
	import Text from './Text.svelte';

	interface Props {
		host: string;
		prompt: string;
	}

	let { host, prompt }: Props = $props();
</script>

<Text as="p" variant="caption">{host}'s prompt: "{prompt}"</Text>
