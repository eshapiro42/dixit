<script lang="ts">
	import type { CardSelection } from '../game/selection.svelte';
	import { gameState } from '../game/state.svelte';
	import Button from './Button.svelte';
	import ConfirmDialog from './ConfirmDialog.svelte';

	let { selection }: { selection: CardSelection } = $props();

	let confirming = $state(false);

	async function confirm(): Promise<void> {
		confirming = false;
		const cardId = selection.selectedId;
		if (!cardId) return;
		await gameState.mulligan(cardId);
		selection.clear();
	}
</script>

<Button kind="ghost" disabled={!selection.selectedId} onclick={() => (confirming = true)}
	>Mulligan</Button
>

<ConfirmDialog
	open={confirming}
	title="Mulligan"
	message="This will discard the selected card and draw a replacement."
	confirmLabel="Mulligan"
	onconfirm={confirm}
	oncancel={() => (confirming = false)}
/>
