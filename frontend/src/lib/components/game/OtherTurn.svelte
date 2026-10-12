<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { PendingAction } from '../../game/pending.svelte';
	import { CardSelection } from '../../game/selection.svelte';
	import { currentPrompt } from '../../game/phase';
	import { gameState } from '../../game/state.svelte';
	import ActionBar from '../ActionBar.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import MulliganControl from '../MulliganControl.svelte';
	import GamePanel from './GamePanel.svelte';

	let { view }: { view: SessionView } = $props();

	const selection = new CardSelection(() => view.hand);
	const submission = new PendingAction();

	let canPlay = $derived(!view.has_played);

	async function submit(): Promise<void> {
		const cardId = selection.selectedId;
		if (!cardId) return;
		await submission.run(() => gameState.play(cardId));
	}
</script>

<GamePanel title="Your Hand" zoomKind="hand" actionNeeded={canPlay} prompt={currentPrompt(view)}>
	<CardRow
		kind="hand"
		cardIds={view.hand}
		selectable={canPlay}
		selectedId={selection.selectedId}
		onselect={(id) => selection.toggle(id)}
	/>
	{#snippet actions()}
		{#if canPlay}
			<ActionBar hint={selection.selectedId ? null : 'Pick the card that best matches the prompt.'}>
				{#snippet primary()}
					<Button disabled={submission.pending || !selection.selectedId} onclick={submit}
						>Submit</Button
					>
				{/snippet}
				{#snippet secondary()}
					{#if view.mulligan_available}
						<MulliganControl {selection} />
					{/if}
				{/snippet}
			</ActionBar>
		{/if}
	{/snippet}
</GamePanel>
