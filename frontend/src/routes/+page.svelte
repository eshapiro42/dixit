<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/Button.svelte';
	import ErrorBanner from '$lib/components/ErrorBanner.svelte';
	import Field from '$lib/components/Field.svelte';
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

	let checkingSession = $state(true);

	onMount(async () => {
		await gameState.tryResume();
		checkingSession = false;
	});

	let mode = $state<'create' | 'join'>('create');
	let playerName = $state('');
	let gameId = $state('');
	let submitting = $state(false);

	async function submitLobbyForm(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		submitting = true;
		if (mode === 'create') {
			await gameState.createGame(playerName);
		} else {
			await gameState.joinGame(gameId.trim().toUpperCase(), playerName);
		}
		submitting = false;
	}

	async function leaveGame(): Promise<void> {
		await gameState.leaveGame();
		gameId = '';
	}

	let showOutcome = $state(false);

	$effect(() => {
		if (gameState.lastOutcome && gameState.outcomeIsFresh) showOutcome = true;
	});

	let view = $derived(gameState.view);
	let isHost = $derived(view !== null && view.host === view.player_name);
</script>

{#if !checkingSession}
	{#if !view}
		<PageShell>
			<div class="lobby">
				<h1>Dixit</h1>

				<ErrorBanner message={gameState.error} ondismiss={() => gameState.clearError()} />

				<div class="tabs" role="tablist">
					<button
						type="button"
						role="tab"
						aria-selected={mode === 'create'}
						onclick={() => (mode = 'create')}>Create a game</button
					>
					<button
						type="button"
						role="tab"
						aria-selected={mode === 'join'}
						onclick={() => (mode = 'join')}>Join a game</button
					>
				</div>

				<form onsubmit={submitLobbyForm}>
					{#if mode === 'join'}
						<Field id="game-id" label="Game code" bind:value={gameId} required maxlength={4} />
					{/if}
					<Field
						id="player-name"
						label="Your name"
						bind:value={playerName}
						required
						maxlength={32}
					/>
					<Button type="submit" disabled={submitting || !playerName.trim()}>
						{mode === 'create' ? 'Create game' : 'Join game'}
					</Button>
				</form>
			</div>
		</PageShell>
	{:else}
		<PageShell>
			<ErrorBanner message={gameState.error} ondismiss={() => gameState.clearError()} />

			<div class="layout">
				<div class="main panel">
					<PromptBar phase={view.phase} host={view.host} prompt={view.prompt} />
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

				<aside class="panel">
					<h2>Scores</h2>
					<ScoreBoard players={view.players} hostName={view.host} />
					<h2>Log</h2>
					<div class="log">
						<MessageLog messages={gameState.messages} />
					</div>
					<div class="leave">
						<Button kind="secondary" onclick={leaveGame}>Leave game</Button>
					</div>
				</aside>
			</div>
		</PageShell>
	{/if}
{/if}

<style>
	.lobby {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 15vh;
		gap: var(--space-2);
	}

	.lobby h1 {
		text-align: center;
	}

	.tabs {
		display: flex;
		gap: var(--space-2);
		margin: var(--space-4) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.tabs button {
		background: none;
		border: none;
		border-bottom: 2px solid transparent;
		padding: var(--space-2) var(--space-1);
		font: inherit;
		font-weight: 600;
		color: var(--color-text-quiet);
		cursor: pointer;
	}

	.tabs button[aria-selected='true'] {
		color: var(--color-text);
		border-bottom-color: var(--color-accent);
	}

	form {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
		max-width: 360px;
	}

	.layout {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: var(--space-6);
		align-items: start;
	}

	@media (min-width: 720px) {
		.layout {
			grid-template-columns: minmax(0, 1fr) 280px;
		}
	}

	.panel {
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-sm);
		padding: var(--space-6);
	}

	aside h2 {
		font-size: var(--size-md);
		margin: 0 0 var(--space-2);
	}

	aside h2:not(:first-child) {
		margin-top: var(--space-4);
	}

	.log {
		max-height: 220px;
	}

	.leave {
		margin-top: var(--space-6);
		padding-top: var(--space-4);
		border-top: 1px solid var(--color-border);
	}
</style>
