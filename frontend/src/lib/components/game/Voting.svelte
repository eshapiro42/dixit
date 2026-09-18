<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import Clue from '../Clue.svelte';
	import Waiting from '../Waiting.svelte';

	let { view }: { view: SessionView } = $props();
	let selected = $state<string | null>(null);
	let submitting = $state(false);

	let isHost = $derived(view.host === view.player_name);

	async function submit(): Promise<void> {
		if (!selected) return;
		submitting = true;
		await gameState.vote(selected);
		submitting = false;
	}
</script>

{#if isHost}
	<Waiting detail="Waiting for votes ({view.votes_cast} of {view.votes_needed})." />
{:else if view.has_voted}
	<Waiting detail="Waiting for the other players to vote." />
{:else}
	<section class="action-needed">
		{#if view.host && view.prompt}
			<Clue host={view.host} prompt={view.prompt} />
		{/if}
		<h2>Table</h2>
		<CardRow
			cardIds={view.table ?? []}
			selectable
			selectedId={selected}
			onselect={(id) => (selected = id)}
		/>
		<Button disabled={submitting || !selected} onclick={submit}>Submit Vote</Button>
	</section>
{/if}
