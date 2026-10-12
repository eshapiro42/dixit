<script lang="ts">
	import BunnyIcon from './BunnyIcon.svelte';
	import Text from './Text.svelte';
</script>

<span class="wordmark">
	<BunnyIcon class="bunny" />
	<Text variant="title" class="word">Dixit</Text>
</span>

<style>
	.wordmark {
		position: relative;
		display: inline-flex;
		align-items: center;
		padding-inline: var(--space-2);
	}

	.wordmark :global(.bunny) {
		position: absolute;
		top: 50%;
		left: 50%;
		height: 3.4em;
		width: auto;
		transform: translate(-50%, -50%);
		fill: var(--color-accent);
		opacity: var(--opacity-faded);
		pointer-events: none;
	}

	.wordmark :global(.word) {
		position: relative;
	}
</style>
