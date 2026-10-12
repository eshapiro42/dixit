<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { startHint } from '../../game/phase';
	import { gameState } from '../../game/state.svelte';
	import Badge from '../Badge.svelte';
	import Button from '../Button.svelte';
	import IconButton from '../IconButton.svelte';
	import InviteCode from '../InviteCode.svelte';
	import PanelHeader from '../PanelHeader.svelte';
	import Text from '../Text.svelte';

	let { view }: { view: SessionView } = $props();

	let hint = $derived(startHint(view));
</script>

<section class="lobby">
	<InviteCode gameId={view.game_id} />

	{#if view.is_creator}
		<div class="start">
			<div class="actions">
				<Button kind="secondary" onclick={() => gameState.addCpu()}>Add CPU</Button>
				<Button disabled={!view.playable} onclick={() => gameState.start()}>Start Game</Button>
			</div>
			{#if hint}<Text as="p" variant="caption">{hint}</Text>{/if}
		</div>
	{:else if hint}
		<Text as="p" variant="caption">{hint}</Text>
	{/if}

	<div>
		<PanelHeader align="baseline">
			<Text variant="heading">Players</Text>
			<Text as="span" variant="label">{view.players.length} joined</Text>
		</PanelHeader>
		<ul class="players">
			{#each view.players as player (player.name)}
				<li class:removable={view.is_creator && player.name !== view.creator_name}>
					<span class="player-name" title={player.name}>{player.name}</span>
					<span class="tags">
						{#if player.is_cpu}<Badge>CPU</Badge>{/if}
						{#if player.name === view.creator_name}<Badge>Creator</Badge>{/if}
						{#if player.name === view.player_name}<Badge tone="solid">You</Badge>{/if}
					</span>
					{#if view.is_creator && player.name !== view.creator_name}
						<IconButton
							icon="close"
							label="Remove {player.name}"
							onclick={() => gameState.removePlayer(player.name)}
						/>
					{/if}
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

	.start {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.start > :global(p) {
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

	/* The remove button brings its own padding. */
	.players li.removable {
		padding-inline-end: var(--space-1);
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
