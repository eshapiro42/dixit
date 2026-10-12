<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Badge from '../Badge.svelte';
	import Button from '../Button.svelte';
	import Divider from '../Divider.svelte';
	import PanelHeader from '../PanelHeader.svelte';
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
	<div class="toolbar">
		{#if view.is_creator}
			<div class="actions">
				<Button kind="secondary" onclick={() => gameState.addCpu()}>Add CPU</Button>
				<Button disabled={!view.playable} onclick={() => gameState.start()}>Start Game</Button>
			</div>
		{/if}

		<div class="invite">
			<Text as="span" variant="label">Game ID</Text>
			<Stat size="hero">{view.game_id}</Stat>
			<Button kind="secondary" onclick={copyGameId}>{copied ? 'Copied!' : 'Copy'}</Button>
		</div>
	</div>

	{#if !view.playable}
		<Text as="p" variant="caption" class="requirement">
			Need at least {view.min_players} players, {view.min_human_players} of them human.
		</Text>
	{/if}

	<Divider spacing="section" />

	<PanelHeader>
		<Text variant="heading">Players</Text>
		<Text as="span" variant="label">{view.players.length} joined</Text>
	</PanelHeader>
	<ul class="players">
		{#each view.players as player (player.name)}
			<li>
				<span class="player-name">{player.name}</span>
				<span class="tags">
					{#if player.is_cpu}<Badge>CPU</Badge>{/if}
					{#if player.name === view.creator_name}<Badge>Creator</Badge>{/if}
					{#if player.name === view.player_name}<Badge tone="solid">You</Badge>{/if}
				</span>
			</li>
		{/each}
	</ul>
</section>

<style>
	.toolbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		flex-wrap: wrap;
		gap: var(--space-3) var(--space-6);
	}

	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
	}

	.invite {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		margin-left: auto;
	}

	section > :global(.requirement) {
		margin-top: var(--space-3);
	}

	.players {
		list-style: none;
		margin: 0;
		padding: 0;
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
		font-weight: var(--weight-medium);
	}

	.tags {
		display: flex;
		gap: var(--space-2);
	}

	.tags :global(.badge) {
		height: 22px;
		padding: 0 var(--space-2);
		font-size: var(--size-xs);
	}
</style>
