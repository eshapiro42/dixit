<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { PendingAction } from '../../game/pending.svelte';
	import { CardSelection } from '../../game/selection.svelte';
	import { currentPrompt } from '../../game/phase';
	import { gameState } from '../../game/state.svelte';
	import ActionBar from '../ActionBar.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import GamePanel from './GamePanel.svelte';

	let { view }: { view: SessionView } = $props();

	const selection = new CardSelection(() => view.table ?? []);
	const submission = new PendingAction();

	let isHost = $derived(view.host === view.player_name);
	let canVote = $derived(!isHost && !view.has_voted);

	async function submit(): Promise<void> {
		const cardId = selection.selectedId;
		if (!cardId) return;
		await submission.run(() => gameState.vote(cardId));
	}
</script>

<GamePanel title="Table" zoomKind="table" actionNeeded={canVote} prompt={currentPrompt(view)}>
	<CardRow
		kind="table"
		cardIds={view.table ?? []}
		selectable={canVote}
		selectedId={selection.selectedId}
		onselect={(id) => selection.toggle(id)}
	/>
	{#snippet actions()}
		{#if canVote}
			<ActionBar
				hint={selection.selectedId ? null : "Pick the card you think is the storyteller's."}
			>
				{#snippet primary()}
					<Button disabled={submission.pending || !selection.selectedId} onclick={submit}
						>Submit Vote</Button
					>
				{/snippet}
			</ActionBar>
		{/if}
	{/snippet}
</GamePanel>
