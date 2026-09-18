<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';

	let { view }: { view: SessionView } = $props();
</script>

<section>
	<ul class="players">
		{#each view.players as player (player.name)}
			<li>{player.name}</li>
		{/each}
	</ul>

	{#if view.is_creator}
		<div class="actions">
			<Button kind="secondary" onclick={() => gameState.addCpu()}>Add CPU</Button>
			<Button disabled={!view.playable} onclick={() => gameState.start()}>Start Game</Button>
		</div>
		{#if !view.playable}
			<p class="quiet">
				Need at least {view.min_players} players, {view.min_human_players} of them human.
			</p>
		{/if}
	{:else}
		<p class="quiet">Waiting for the host to start the game.</p>
	{/if}
</section>

<style>
	.players {
		list-style: none;
		margin: var(--space-4) 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--space-1);
	}

	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
	}
</style>
