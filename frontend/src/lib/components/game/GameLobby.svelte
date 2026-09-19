<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import Stat from '../Stat.svelte';
	import Text from '../Text.svelte';

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
		<Text as="span" variant="label">Game ID</Text>
		<div class="invite-row">
			<Stat size="hero">{view.game_id}</Stat>
			<Button kind="secondary" onclick={copyGameId}>{copied ? 'Copied!' : 'Copy'}</Button>
		</div>
	</div>

	{#if view.is_creator}
		<div class="actions">
			<Button kind="secondary" onclick={() => gameState.addCpu()}>Add CPU</Button>
			<Button disabled={!view.playable} onclick={() => gameState.start()}>Start Game</Button>
		</div>
	{:else}
		<Text as="p" variant="caption">Waiting for the creator to start the game.</Text>
	{/if}
	{#if !view.playable}
		<Text as="p" variant="caption">
			Need at least {view.min_players} players, {view.min_human_players} of them human.
		</Text>
	{/if}

	<ul class="players">
		{#each view.players as player (player.name)}
			<li>
				{player.name}
				{#if player.name === view.player_name}<Text as="span" variant="tag">· You</Text>{/if}
				{#if player.name === view.creator_name}<Text as="span" variant="tag">· Creator</Text>{/if}
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

	.players {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.players li {
		padding: var(--space-2) 0;
	}

	.players li + li {
		border-top: var(--border-width) solid var(--color-border);
	}

	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
		margin-bottom: var(--space-3);
	}

	section > :global(p) {
		margin: 0 0 var(--space-3);
	}
</style>
