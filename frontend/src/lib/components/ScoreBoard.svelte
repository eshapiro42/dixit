<script lang="ts">
	import type { PlayerSummary } from '../api/types';

	interface Props {
		players: PlayerSummary[];
		hostName?: string | null;
	}

	let { players, hostName = null }: Props = $props();

	let ranked = $derived([...players].sort((a, b) => b.score - a.score));
</script>

<ul class="scoreboard">
	{#each ranked as player (player.name)}
		<li>
			<span class="name">
				{player.name}
				{#if player.name === hostName}
					<span class="badge" title="Storyteller this round">✎</span>
				{/if}
				{#if player.is_cpu}<span class="quiet">· CPU</span>{/if}
			</span>
			<span class="score numeric">{player.score}</span>
		</li>
	{/each}
</ul>

<style>
	.scoreboard {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--space-1);
	}

	li {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: var(--space-2) var(--space-3);
		border-radius: var(--radius-sm);
	}

	li:nth-child(odd) {
		background: color-mix(in srgb, var(--color-border) 35%, transparent);
	}

	.name {
		font-size: var(--size-sm);
	}

	.badge {
		color: var(--color-accent);
	}

	.score {
		font-weight: 600;
	}
</style>
