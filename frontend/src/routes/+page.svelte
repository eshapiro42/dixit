<script lang="ts">
	import { onMount } from 'svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
	import Dialog from '$lib/components/Dialog.svelte';
	import ErrorBanner from '$lib/components/ErrorBanner.svelte';
	import LobbyForm from '$lib/components/LobbyForm.svelte';
	import MessageLog from '$lib/components/MessageLog.svelte';
	import PageShell from '$lib/components/PageShell.svelte';
	import TopBar from '$lib/components/TopBar.svelte';
	import GameLobby from '$lib/components/game/GameLobby.svelte';
	import GameScreen from '$lib/components/game/GameScreen.svelte';
	import { gameState } from '$lib/game/state.svelte';

	let checkingSession = $state(true);

	onMount(async () => {
		await gameState.tryResume();
		checkingSession = false;
	});

	let confirmingLeave = $state(false);
	let logOpen = $state(false);
	let view = $derived(gameState.view);

	async function confirmLeave(): Promise<void> {
		confirmingLeave = false;
		await gameState.leaveGame();
	}

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
	<TopBar {view} onOpenLog={() => (logOpen = true)} onLeave={() => (confirmingLeave = true)} />

	{#if !view}
		<PageShell>
			<LobbyForm />
		</PageShell>
	{:else}
		<PageShell wide>
			<ErrorBanner message={gameState.error} ondismiss={() => gameState.clearError()} />

			{#if !view.started}
				<GameLobby {view} />
			{:else}
				<GameScreen {view} />
			{/if}
		</PageShell>

		<Dialog title="Game Log" open={logOpen} wide onclose={() => (logOpen = false)}>
			<MessageLog messages={gameState.messages} outcomes={gameState.outcomes} open={logOpen} />
		</Dialog>

		<ConfirmDialog
			open={confirmingLeave}
			title="Leave Game"
			message="You'll return to the lobby form and can rejoin later with the same name and game ID."
			confirmLabel="Leave Game"
			onconfirm={confirmLeave}
			oncancel={() => (confirmingLeave = false)}
		/>
	{/if}
{/if}
