<script lang="ts">
	interface Props {
		host: string;
		prompt: string;
	}

	let { host, prompt }: Props = $props();
</script>

<p class="clue"><span class="quiet">{host}'s clue:</span> "{prompt}"</p>

<style>
	.clue {
		margin: 0 0 var(--space-4);
		font-size: var(--size-lg);
		font-weight: 600;
	}
</style>
