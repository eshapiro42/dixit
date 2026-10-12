<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { PendingAction } from '../../game/pending.svelte';
	import { CardSelection } from '../../game/selection.svelte';
	import { gameState } from '../../game/state.svelte';
	import ActionBar from '../ActionBar.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import Field from '../Field.svelte';
	import MulliganControl from '../MulliganControl.svelte';
	import GamePanel from './GamePanel.svelte';

	let { view }: { view: SessionView } = $props();

	const promptId = $props.id();
	const selection = new CardSelection(
		() => view.hand,
		() => (prompt = '')
	);
	const submission = new PendingAction();
	let prompt = $state('');

	let hint = $derived(
		!selection.selectedId
			? 'Pick a card from your hand.'
			: !prompt.trim()
				? 'Write a prompt for your card.'
				: null
	);

	async function submit(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		const cardId = selection.selectedId;
		if (!cardId || !prompt.trim()) return;
		await submission.run(() => gameState.hostChoice(cardId, prompt.trim()));
	}
</script>

<GamePanel title="Your Hand" zoomKind="hand" actionNeeded>
	<CardRow
		kind="hand"
		cardIds={view.hand}
		selectable
		selectedId={selection.selectedId}
		onselect={(id) => selection.toggle(id)}
	/>

	<form onsubmit={submit}>
		<Field
			id={promptId}
			label="Your prompt"
			hideLabel
			bind:value={prompt}
			placeholder="Your prompt"
			maxlength={200}
			required
			enterkeyhint="send"
		/>
		<ActionBar {hint}>
			{#snippet primary()}
				<Button
					type="submit"
					disabled={submission.pending || !selection.selectedId || !prompt.trim()}>Submit</Button
				>
			{/snippet}
			{#snippet secondary()}
				{#if view.mulligan_available}
					<MulliganControl {selection} />
				{/if}
			{/snippet}
		</ActionBar>
	</form>
</GamePanel>

<style>
	form {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}
</style>
