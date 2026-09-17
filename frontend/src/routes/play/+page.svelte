<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import ErrorBanner from '$lib/components/ErrorBanner.svelte';
	import MessageLog from '$lib/components/MessageLog.svelte';
	import PageShell from '$lib/components/PageShell.svelte';
	import PromptBar from '$lib/components/PromptBar.svelte';
	import ScoreBoard from '$lib/components/ScoreBoard.svelte';
	import GameLobby from '$lib/components/game/GameLobby.svelte';
	import HostTurn from '$lib/components/game/HostTurn.svelte';
	import Outcome from '$lib/components/game/Outcome.svelte';
	import OtherTurn from '$lib/components/game/OtherTurn.svelte';
	import Voting from '$lib/components/game/Voting.svelte';
	import { gameState } from '$lib/game/state.svelte';

	let ready = $state(false);
	let showOutcome = $state(false);

	onMount(async () => {
		if (!gameState.inGame) {
			await gameState.refresh();
		}
		if (!gameState.inGame) {
			await goto(resolve('/'));
			return;
		}
		ready = true;
	});

	$effect(() => {
		if (gameState.lastOutcome) showOutcome = true;
	});

	let view = $derived(gameState.view);
	let isHost = $derived(view !== null && view.host === view.player_name);
</script>

<PageShell>
	{#if ready && view}
		<PromptBar phase={view.phase} host={view.host} prompt={view.prompt} />
		<ErrorBanner message={gameState.error} ondismiss={() => gameState.clearError()} />

		<div class="layout">
			<div class="main">
				{#if showOutcome && gameState.lastOutcome}
					<Outcome outcome={gameState.lastOutcome} ondismiss={() => (showOutcome = false)} />
				{:else if !view.started}
					<GameLobby {view} />
				{:else if view.phase === 'host_choosing'}
					{#if isHost}
						<HostTurn {view} />
					{:else}
						<section>
							<h2>Waiting</h2>
							<p class="quiet">{view.host} is choosing a card and a prompt.</p>
						</section>
					{/if}
				{:else if view.phase === 'others_choosing'}
					{#if isHost}
						<section>
							<h2>Waiting</h2>
							<p class="quiet">Other players are matching your prompt.</p>
						</section>
					{:else}
						<OtherTurn {view} />
					{/if}
				{:else if view.phase === 'voting'}
					<Voting {view} />
				{/if}
			</div>

			<aside>
				<h2>Scores</h2>
				<ScoreBoard players={view.players} hostName={view.host} />
				<h2>Log</h2>
				<div class="log">
					<MessageLog messages={gameState.messages} />
				</div>
			</aside>
		</div>
	{/if}
</PageShell>

<style>
	.layout {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: var(--space-6);
	}

	@media (min-width: 720px) {
		.layout {
			grid-template-columns: minmax(0, 1fr) 260px;
		}
	}

	aside h2 {
		font-size: var(--size-md);
		margin-top: var(--space-4);
	}

	.log {
		max-height: 220px;
	}
</style>
