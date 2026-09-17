<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';

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
	<section>
		<h2>Votes are coming in</h2>
		<p class="quiet">You wrote this round's prompt, so you don't vote.</p>
	</section>
{:else if view.has_voted}
	<section>
		<h2>Vote cast</h2>
		<p class="quiet">Waiting for the other players to vote.</p>
	</section>
{:else}
	<section>
		<h2>Which card matches "{view.prompt}"?</h2>
		<CardRow
			cardIds={view.table ?? []}
			selectable
			selectedId={selected}
			onselect={(id) => (selected = id)}
		/>
		<Button disabled={submitting || !selected} onclick={submit}>Vote</Button>
	</section>
{/if}
