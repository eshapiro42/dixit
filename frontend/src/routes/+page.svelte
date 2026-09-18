<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/Button.svelte';
	import Dialog from '$lib/components/Dialog.svelte';
	import ErrorBanner from '$lib/components/ErrorBanner.svelte';
	import Field from '$lib/components/Field.svelte';
	import MessageLog from '$lib/components/MessageLog.svelte';
	import PageShell from '$lib/components/PageShell.svelte';
	import ScoreBoard from '$lib/components/ScoreBoard.svelte';
	import TopBar from '$lib/components/TopBar.svelte';
	import Waiting from '$lib/components/Waiting.svelte';
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
		if (!confirm('Leave the game?')) return;
		await gameState.leaveGame();
		gameId = '';
	}

	let logOpen = $state(false);

	let view = $derived(gameState.view);
	let isHost = $derived(view !== null && view.host === view.player_name);

	$effect(() => {
		if (!view) return;
		function confirmClose(event: BeforeUnloadEvent): void {
			event.preventDefault();
			event.returnValue = '';
		}
		window.addEventListener('beforeunload', confirmClose);
		return () => window.removeEventListener('beforeunload', confirmClose);
	});
</script>

{#if !checkingSession}
	<TopBar {view} onOpenLog={() => (logOpen = true)} onLeave={leaveGame} />

	{#if !view}
		<PageShell>
			<div class="lobby">
				<ErrorBanner message={gameState.error} ondismiss={() => gameState.clearError()} />

				<div class="tabs" role="tablist">
					<button
						type="button"
						role="tab"
						aria-selected={mode === 'create'}
						onclick={() => (mode = 'create')}>Create a New Game</button
					>
					<button
						type="button"
						role="tab"
						aria-selected={mode === 'join'}
						onclick={() => (mode = 'join')}>Join a Game</button
					>
				</div>

				<form onsubmit={submitLobbyForm}>
					{#if mode === 'join'}
						<Field id="game-id" label="Game ID" bind:value={gameId} required maxlength={4} />
					{/if}
					<Field
						id="player-name"
						label="Your Name"
						bind:value={playerName}
						required
						maxlength={32}
					/>
					<Button type="submit" disabled={submitting || !playerName.trim()}>
						{mode === 'create' ? "Let's Move It" : "Let's Groove It"}
					</Button>
				</form>
			</div>
		</PageShell>
	{:else}
		<PageShell wide>
			<ErrorBanner message={gameState.error} ondismiss={() => gameState.clearError()} />

			<div class="board panel">
				{#if !view.started}
					<GameLobby {view} />
				{:else}
					{#if view.phase === 'host_choosing'}
						{#if isHost}
							<HostTurn {view} />
						{:else}
							<Waiting detail="Waiting for {view.host} to write a prompt." />
						{/if}
					{:else if view.phase === 'others_choosing'}
						{#if isHost}
							<Waiting detail="Waiting for the other players to choose a card." />
						{:else}
							<OtherTurn {view} />
						{/if}
					{:else if view.phase === 'voting'}
						<Voting {view} />
					{/if}

					{#if view.phase !== 'voting' && gameState.lastOutcome}
						<Outcome outcome={gameState.lastOutcome} players={view.players} />
					{/if}
				{/if}
			</div>

			{#if view.started}
				<div class="panel score-panel">
					<ScoreBoard players={view.players} hostName={view.host} />
				</div>
			{/if}

			<Dialog title="Game Log" open={logOpen} onclose={() => (logOpen = false)}>
				<MessageLog messages={gameState.messages} />
			</Dialog>
		</PageShell>
	{/if}
{/if}

<style>
	.lobby {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 10vh;
		gap: var(--space-2);
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

	.panel {
		background: var(--color-surface);
		padding: var(--space-6);
	}

	.board {
		margin-bottom: var(--space-6);
	}

	.score-panel {
		padding: var(--space-4) var(--space-6);
	}

	@media (max-width: 480px) {
		.panel {
			padding: var(--space-4);
		}

		.score-panel {
			padding: var(--space-3) var(--space-4);
		}
	}
</style>
