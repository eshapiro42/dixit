<script lang="ts">
	import { onMount } from 'svelte';
	import BrandHeader from '$lib/components/BrandHeader.svelte';
	import Button from '$lib/components/Button.svelte';
	import Dialog from '$lib/components/Dialog.svelte';
	import ErrorBanner from '$lib/components/ErrorBanner.svelte';
	import Field from '$lib/components/Field.svelte';
	import MessageLog from '$lib/components/MessageLog.svelte';
	import PageShell from '$lib/components/PageShell.svelte';
	import PromptBar from '$lib/components/PromptBar.svelte';
	import ScoreBoard from '$lib/components/ScoreBoard.svelte';
	import ZoomControl from '$lib/components/ZoomControl.svelte';
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
	{#if !view}
		<PageShell>
			<BrandHeader />
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
						{mode === 'create' ? "Let's Groove It" : "Let's Move It"}
					</Button>
				</form>
			</div>
		</PageShell>
	{:else}
		<PageShell wide>
			<BrandHeader />
			<ErrorBanner message={gameState.error} ondismiss={() => gameState.clearError()} />

			<div class="board panel">
				<div class="board-header">
					<PromptBar phase={view.phase} host={view.host} prompt={view.prompt} />
					<div class="board-actions">
						{#if view.started}
							<ZoomControl />
						{/if}
						<Button kind="secondary" onclick={() => (logOpen = true)}>Game Log</Button>
						<Button kind="ghost" onclick={leaveGame}>Leave Game</Button>
					</div>
				</div>

				{#if !view.started}
					<GameLobby {view} />
				{:else}
					{#if view.phase === 'host_choosing'}
						{#if isHost}
							<HostTurn {view} />
						{:else}
							<section>
								<h2>Waiting</h2>
							</section>
						{/if}
					{:else if view.phase === 'others_choosing'}
						{#if isHost}
							<section>
								<h2>Waiting</h2>
							</section>
						{:else}
							<OtherTurn {view} />
						{/if}
					{:else if view.phase === 'voting'}
						<Voting {view} />
					{/if}

					{#if view.phase !== 'voting' && gameState.lastOutcome}
						<Outcome outcome={gameState.lastOutcome} />
					{/if}
				{/if}
			</div>

			<div class="panel score-panel">
				<ScoreBoard players={view.players} hostName={view.host} />
			</div>

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
		padding-top: 15vh;
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
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-sm);
		padding: var(--space-6);
	}

	.board {
		margin-bottom: var(--space-6);
	}

	.board-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		flex-wrap: wrap;
		gap: var(--space-3);
		border-bottom: 1px solid var(--color-border);
		padding-bottom: var(--space-3);
		margin-bottom: var(--space-4);
	}

	.board-actions {
		display: flex;
		gap: var(--space-2);
		flex-shrink: 0;
	}

	.score-panel {
		padding: var(--space-4) var(--space-6);
	}
</style>
