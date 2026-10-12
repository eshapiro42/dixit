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

	let ranked = $derived([...players].sort((a, b) => b.score - a.score));
</script>

<PanelHeader>
	<Text variant="heading">Player Scores</Text>
</PanelHeader>
<!-- A real <table> lays out columns as equal-width slots (or auto-sized ones
     that still don't support gap-based distribution) - neither gives every
     entry its own natural width while spacing them like flexbox/grid
     space-between. Built as a grid instead, with explicit ARIA table roles
     since the row groupings are visual grid tracks now, not <tr> elements. -->
<div class="scores" role="table">
	<div class="scores-row" role="row">
		{#each ranked as player, index (player.name)}
			<div
				class="scores-cell scores-cell--header"
				role="columnheader"
				style:grid-row="1"
				style:grid-column={index + 1}
			>
				{#if player.name === hostName}
					<BunnyIcon class="storyteller-badge" />
					<span class="sr-only">Storyteller</span>
				{/if}
				<span class="player-name">{player.name}</span>
			</div>
		{/each}
	</div>
	<div class="scores-row" role="row">
		{#each ranked as player, index (player.name)}
			<div class="scores-cell" role="cell" style:grid-row="2" style:grid-column={index + 1}>
				{#if player.is_cpu}
					<span class="score-na" aria-hidden="true">&ndash;</span>
					<span class="sr-only">CPUs don't score points</span>
				{:else}
					<span class="score-cell">
						<Stat>{player.score}</Stat>
						{#if deltas?.[player.name] !== undefined}
							<Badge tone="solid" size="delta" class="delta">+{deltas[player.name]}</Badge>
						{/if}
					</span>
				{/if}
			</div>
		{/each}
	</div>
</div>

<style>
	.scores {
		display: grid;
		grid-auto-columns: max-content;
		justify-content: space-between;
		column-gap: var(--space-4);
		row-gap: var(--space-2);
		overflow-x: auto;
	}

	/* display: contents keeps role="row" for assistive tech while the cells become the grid items. */
	.scores-row {
		display: contents;
	}

	.scores-cell {
		text-align: center;
		white-space: nowrap;
	}

	/* Bottom-aligned so names share a baseline whether or not a storyteller badge sits above. */
	.scores-cell--header {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: flex-end;
		font-size: var(--size-md);
		font-weight: var(--weight-medium);
	}

	.score-na {
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		color: var(--color-text-quiet);
	}

	.scores-cell :global(.storyteller-badge) {
		height: 1.3em;
		width: auto;
		margin-bottom: var(--space-1);
		fill: var(--color-accent);
	}

	.score-cell {
		display: inline-flex;
		align-items: center;
		gap: var(--space-1);
	}

	@media (max-width: 480px) {
		.scores {
			column-gap: var(--space-3);
		}
	}
</style>
