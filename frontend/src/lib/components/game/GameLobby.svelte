<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Badge from '../Badge.svelte';
	import Button from '../Button.svelte';
	import InviteCode from '../InviteCode.svelte';
	import PanelHeader from '../PanelHeader.svelte';
	import Text from '../Text.svelte';

	let { view }: { view: SessionView } = $props();
</script>

<section class="lobby">
	<InviteCode gameId={view.game_id} />

	{#if view.is_creator}
		<div class="actions">
			<Button kind="secondary" onclick={() => gameState.addCpu()}>Add CPU</Button>
			<Button disabled={!view.playable} onclick={() => gameState.start()}>Start Game</Button>
		</div>
	{/if}
	{#if !view.playable}
		<Text as="p" variant="caption">
			Need at least {view.min_players} players, {view.min_human_players} of them human.
		</Text>
	{/if}

	<div>
		<PanelHeader align="baseline">
			<Text variant="heading">Players</Text>
			<Text as="span" variant="label">{view.players.length} joined</Text>
		</PanelHeader>
		<ul class="players">
			{#each view.players as player (player.name)}
				<li>
					<span class="player-name" title={player.name}>{player.name}</span>
					<span class="tags">
						{#if player.is_cpu}<Badge>CPU</Badge>{/if}
						{#if player.name === view.creator_name}<Badge>Creator</Badge>{/if}
						{#if player.name === view.player_name}<Badge tone="solid">You</Badge>{/if}
					</span>
				</li>
			{/each}
		</ul>
	</div>
</section>

<style>
	.lobby {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
		max-width: var(--measure-lobby);
		margin: 0 auto;
	}

	.lobby > :global(p) {
		margin: 0;
	}

	.actions {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-3);
	}

	.players {
		margin: 0;
		padding: 0;
		list-style: none;
		border-top: var(--border-width) solid var(--color-border);
	}

	.players li {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-3);
		min-height: var(--tap);
		padding: var(--space-2) var(--space-3);
		border-bottom: var(--border-width) solid var(--color-border);
	}

	.player-name {
		min-width: 0;
		overflow: hidden;
		font-weight: var(--weight-medium);
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.tags {
		display: flex;
		flex-shrink: 0;
		gap: var(--space-2);
	}

	.tags :global(.badge) {
		height: 22px;
		padding: 0 var(--space-2);
		font-size: var(--size-xs);
	}
</style>
