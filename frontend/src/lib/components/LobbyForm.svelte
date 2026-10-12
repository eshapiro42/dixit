<script lang="ts">
	import { replaceState } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { onMount } from 'svelte';
	import { gameIdFromUrl } from '../game/invite';
	import { gameState } from '../game/state.svelte';
	import Button from './Button.svelte';
	import ErrorBanner from './ErrorBanner.svelte';
	import Field from './Field.svelte';
	import Tabs from './Tabs.svelte';

	type Mode = 'create' | 'join';

	const TABS: { id: Mode; label: string }[] = [
		{ id: 'create', label: 'Create a New Game' },
		{ id: 'join', label: 'Join a Game' }
	];

	let mode = $state<Mode>('create');
	let playerName = $state('');
	let gameId = $state('');
	let submitting = $state(false);

	let canSubmit = $derived(
		!submitting && playerName.trim() !== '' && (mode === 'create' || gameId.trim() !== '')
	);

	// A shared join link opens straight onto the Join tab with the code filled in.
	onMount(() => {
		const fromLink = gameIdFromUrl(window.location.search);
		if (fromLink) {
			gameId = fromLink;
			mode = 'join';
		}
	});

	function clearJoinLink(): void {
		if (window.location.search) replaceState(resolve('/'), {});
	}

	async function submit(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		submitting = true;
		if (mode === 'create') {
			await gameState.createGame(playerName);
		} else {
			await gameState.joinGame(gameId.trim().toUpperCase(), playerName);
		}
		submitting = false;
		if (gameState.view) clearJoinLink();
	}
</script>

<div class="lobby-form">
	<Tabs tabs={TABS} bind:value={mode} label="Game options" onchange={() => gameState.clearError()}>
		<form onsubmit={submit}>
			{#if mode === 'join'}
				<Field
					id="game-id"
					label="Game ID"
					bind:value={gameId}
					required
					maxlength={4}
					autocapitalize="characters"
					autocorrect="off"
					spellcheck={false}
					class="game-id-input"
					oninput={() => gameState.clearError()}
				/>
			{/if}
			<Field
				id="player-name"
				label="Your Name"
				bind:value={playerName}
				required
				maxlength={32}
				autocapitalize="words"
				enterkeyhint="go"
				oninput={() => gameState.clearError()}
			/>
			<ErrorBanner message={gameState.error} ondismiss={() => gameState.clearError()} />
			<Button type="submit" disabled={!canSubmit}>
				{mode === 'create' ? "Let's Move It" : "Let's Groove It"}
			</Button>
		</form>
	</Tabs>
</div>

<style>
	.lobby-form {
		width: 100%;
		max-width: var(--measure-form);
		margin: 0 auto;
		padding-top: clamp(var(--space-4), 8dvh, 6rem);
	}

	form {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
		padding-top: var(--space-4);
	}

	form :global(.game-id-input) {
		font-family: var(--font-mono);
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
</style>
