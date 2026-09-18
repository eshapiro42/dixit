<script lang="ts">
	import { gameState } from '../game/state.svelte';

	let gameId = $derived(gameState.view?.game_id ?? null);
</script>

<header class="brand">
	<span class="wordmark">Dixit</span>
	{#if gameId}<span class="quiet numeric">Game ID: {gameId}</span>{/if}
</header>

<style>
	.brand {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: var(--space-3);
		margin-bottom: var(--space-4);
	}

	.wordmark {
		font-family: var(--font-serif);
		font-weight: 600;
		font-size: var(--size-md);
	}
</style>
