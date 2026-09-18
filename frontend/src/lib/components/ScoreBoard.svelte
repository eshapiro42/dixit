<script lang="ts">
	import type { PlayerSummary } from '../api/types';

	interface Props {
		players: PlayerSummary[];
		hostName?: string | null;
	}

	let { players, hostName = null }: Props = $props();

	let ranked = $derived([...players].sort((a, b) => b.score - a.score));
</script>

<h2>Player Scores</h2>
<div class="scores">
	<table>
		<thead>
			<tr>
				{#each ranked as player (player.name)}
					<th>
						{player.name}
						{#if player.name === hostName}<span class="quiet"> · Storyteller</span>{/if}
					</th>
				{/each}
			</tr>
		</thead>
		<tbody>
			<tr>
				{#each ranked as player (player.name)}
					<td class="numeric">{player.score}</td>
				{/each}
			</tr>
		</tbody>
	</table>
</div>

<style>
	h2 {
		margin-bottom: var(--space-3);
	}

	.scores {
		overflow-x: auto;
	}

	table {
		width: 100%;
		table-layout: fixed;
		border-collapse: collapse;
	}

	th,
	td {
		width: 1%;
		padding: var(--space-2) var(--space-4);
		text-align: center;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	th {
		font-size: var(--size-sm);
		font-weight: 600;
		border-bottom: 1px solid var(--color-border);
	}

	td {
		font-weight: 600;
		font-size: var(--size-lg);
	}

	/* Equal-width columns look good with a handful of players, but crush names
	 * once there are many on a narrow screen; fall back to natural sizing plus
	 * horizontal scroll instead of shrinking text to fit.
	 */
	@media (max-width: 480px) {
		table {
			table-layout: auto;
		}

		th,
		td {
			width: auto;
			padding: var(--space-2) var(--space-3);
		}
	}
</style>
