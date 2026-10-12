<script lang="ts">
	import type { PlayerSummary } from '../api/types';
	import Badge from './Badge.svelte';
	import BunnyIcon from './BunnyIcon.svelte';
	import PanelHeader from './PanelHeader.svelte';
	import Stat from './Stat.svelte';
	import Text from './Text.svelte';

	interface Props {
		players: PlayerSummary[];
		hostName?: string | null;
		deltas?: Record<string, number>;
	}

	let { players, hostName = null, deltas }: Props = $props();

	// CPUs never score, so they trail the ranked humans without a rank.
	let ordered = $derived([
		...players.filter((p) => !p.is_cpu).sort((a, b) => b.score - a.score),
		...players.filter((p) => p.is_cpu)
	]);
</script>

<PanelHeader>
	<Text variant="heading">Player Scores</Text>
</PanelHeader>
<div class="scoreboard">
	<!-- One list, two layouts: a ranked list when narrow, one column per player when wide. -->
	<ol class="scores" role="list" aria-label="Player scores">
		{#each ordered as player, index (player.name)}
			<li class="entry">
				<span class="rank" aria-hidden="true">{player.is_cpu ? '' : index + 1}</span>
				<span class="who">
					{#if player.name === hostName}
						<BunnyIcon class="storyteller-badge" />
						<span class="sr-only">Storyteller</span>
					{/if}
					<span class="player-name" title={player.name}>{player.name}</span>
				</span>
				<span class="points">
					{#if player.is_cpu}
						<span class="score-na" aria-hidden="true">&ndash;</span>
						<span class="sr-only">CPUs don't score points</span>
					{:else}
						<Stat>{player.score}</Stat>
						{#if deltas?.[player.name] !== undefined}
							<Badge tone="solid" size="delta" class="delta">+{deltas[player.name]}</Badge>
						{/if}
					{/if}
				</span>
			</li>
		{/each}
	</ol>
</div>

<style>
	.scoreboard {
		container-type: inline-size;
	}

	.scores {
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.entry {
		display: grid;
		grid-template-columns: var(--size-lg) minmax(0, 1fr) auto;
		align-items: center;
		gap: var(--space-3);
		min-height: var(--tap);
		border-top: var(--border-width) solid var(--color-border);
	}

	.entry:last-child {
		border-bottom: var(--border-width) solid var(--color-border);
	}

	.rank {
		color: var(--color-text-quiet);
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		text-align: center;
	}

	.who {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		min-width: 0;
		font-weight: var(--weight-medium);
	}

	.player-name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.points {
		display: inline-flex;
		align-items: center;
		gap: var(--space-1);
		min-height: 1.5rem;
	}

	.score-na {
		color: var(--color-text-quiet);
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
	}

	.who :global(.storyteller-badge) {
		flex-shrink: 0;
		height: 1.1em;
		width: auto;
		fill: var(--color-accent);
	}

	@container (min-width: 40rem) {
		.scores {
			display: flex;
			align-items: flex-end;
			justify-content: space-between;
			gap: var(--space-4);
		}

		.entry {
			display: flex;
			flex-direction: column;
			align-items: center;
			gap: var(--space-2);
			min-height: 0;
			min-width: 0;
			border: none;
		}

		.entry:last-child {
			border: none;
		}

		.rank {
			display: none;
		}

		.who {
			flex-direction: column;
			gap: var(--space-1);
			max-width: 14rem;
		}

		.who :global(.storyteller-badge) {
			height: 1.3em;
		}
	}
</style>
