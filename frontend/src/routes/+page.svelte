<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import Button from '$lib/components/Button.svelte';
	import ErrorBanner from '$lib/components/ErrorBanner.svelte';
	import Field from '$lib/components/Field.svelte';
	import PageShell from '$lib/components/PageShell.svelte';
	import { gameState } from '$lib/game/state.svelte';

	let mode = $state<'create' | 'join'>('create');
	let playerName = $state('');
	let gameId = $state('');
	let submitting = $state(false);
	let checkingSession = $state(true);

	onMount(async () => {
		await gameState.refresh();
		if (gameState.inGame) {
			await goto(resolve('/play'));
			return;
		}
		checkingSession = false;
	});

	async function submit(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		submitting = true;
		if (mode === 'create') {
			await gameState.createGame(playerName);
		} else {
			await gameState.joinGame(gameId.trim().toUpperCase(), playerName);
		}
		submitting = false;
		if (gameState.inGame) await goto(resolve('/play'));
	}
</script>

<PageShell>
	{#if !checkingSession}
		<h1>Dixit</h1>
		<p class="quiet">Gather storytellers, then create or join a game.</p>

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

		<form onsubmit={submit}>
			{#if mode === 'join'}
				<Field id="game-id" label="Game code" bind:value={gameId} required maxlength={4} />
			{/if}
			<Field id="player-name" label="Your name" bind:value={playerName} required maxlength={32} />
			<Button type="submit" disabled={submitting || !playerName.trim()}>
				{mode === 'create' ? 'Create game' : 'Join game'}
			</Button>
		</form>
	{/if}
</PageShell>

<style>
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
</style>
