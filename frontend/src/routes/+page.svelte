<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/Button.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
	import Dialog from '$lib/components/Dialog.svelte';
	import Divider from '$lib/components/Divider.svelte';
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
	import YourHandPanel from '$lib/components/game/YourHandPanel.svelte';
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

	let confirmingLeave = $state(false);

	function askLeave(): void {
		confirmingLeave = true;
	}

	async function confirmLeave(): Promise<void> {
		confirmingLeave = false;
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
	<TopBar {view} onOpenLog={() => (logOpen = true)} onLeave={askLeave} />

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

			<div class="panel">
				{#if !view.started}
					<GameLobby {view} />
				{:else}
					{#if view.phase === 'host_choosing'}
						{#if isHost}
							<HostTurn {view} />
						{:else}
							<YourHandPanel {view} />
							<Divider spacing="section" />
							<Waiting detail="Waiting for {view.host} to write a prompt." />
						{/if}
					{:else if view.phase === 'others_choosing'}
						{#if isHost}
							<YourHandPanel {view} />
							<Divider spacing="section" />
							<Waiting detail="Waiting for the other players to choose a card." />
						{:else}
							<OtherTurn {view} />
						{/if}
					{:else if view.phase === 'voting'}
						<YourHandPanel {view} />
						<Divider spacing="section" />
						<Voting {view} />
					{/if}

					{#if view.phase !== 'voting' && gameState.lastOutcome}
						<Outcome outcome={gameState.lastOutcome} players={view.players} />
					{/if}

					<Divider spacing="section" />
					<ScoreBoard
						players={view.players}
						hostName={view.host}
						deltas={gameState.lastOutcome?.scores}
					/>
				{/if}
			</div>

			<Dialog title="Game Log" open={logOpen} wide onclose={() => (logOpen = false)}>
				<MessageLog messages={gameState.messages} open={logOpen} />
			</Dialog>

			<ConfirmDialog
				open={confirmingLeave}
				title="Leave Game"
				message="You'll return to the lobby form and can rejoin later with the same name and game ID."
				confirmLabel="Leave Game"
				onconfirm={confirmLeave}
				oncancel={() => (confirmingLeave = false)}
			/>
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
		font-family: inherit;
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		color: var(--color-text-quiet);
		cursor: pointer;
	}

	.tabs button[aria-selected='true'] {
		color: var(--color-text);
		font-weight: var(--weight-bold);
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

	@media (max-width: 480px) {
		.panel {
			padding: var(--space-4);
		}
	}
</style>
