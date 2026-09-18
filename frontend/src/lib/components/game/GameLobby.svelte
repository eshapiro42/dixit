<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';

	let { view }: { view: SessionView } = $props();

	let copied = $state(false);
	let copyTimeout: ReturnType<typeof setTimeout> | undefined;

	async function copyGameId(): Promise<void> {
		try {
			await navigator.clipboard.writeText(view.game_id);
		} catch {
			return;
		}
		copied = true;
		clearTimeout(copyTimeout);
		copyTimeout = setTimeout(() => (copied = false), 1500);
	}
</script>

<section>
	<div class="invite">
		<span class="quiet">Game ID</span>
		<div class="invite-row">
			<span class="code numeric">{view.game_id}</span>
			<Button kind="secondary" onclick={copyGameId}>{copied ? 'Copied!' : 'Copy'}</Button>
		</div>
	</div>

	{#if view.is_creator}
		<div class="actions">
			<Button kind="secondary" onclick={() => gameState.addCpu()}>Add CPU</Button>
			<Button disabled={!view.playable} onclick={() => gameState.start()}>Start Game</Button>
		</div>
	{:else}
		<p class="quiet">Waiting for the creator to start the game.</p>
	{/if}
	{#if !view.playable}
		<p class="quiet">
			Need at least {view.min_players} players, {view.min_human_players} of them human.
		</p>
	{/if}

	<ul class="players">
		{#each view.players as player (player.name)}
			<li>
				{player.name}
				{#if player.name === view.player_name}<span class="quiet"> · You</span>{/if}
				{#if player.name === view.creator_name}<span class="quiet"> · Creator</span>{/if}
			</li>
		{/each}
	</ul>
</section>

<style>
	.invite {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		margin-bottom: var(--space-4);
	}

	.invite-row {
		display: flex;
		align-items: center;
		gap: var(--space-3);
	}

	.code {
		font-family: var(--font-mono);
		font-size: var(--size-2xl);
		font-weight: 600;
		letter-spacing: 0.05em;
	}

	.players {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.players li {
		padding: var(--space-2) 0;
	}

	.players li + li {
		border-top: 1px solid var(--color-border);
	}

	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
		margin-bottom: var(--space-3);
	}

	section > p {
		margin: 0 0 var(--space-3);
	}
</style>
