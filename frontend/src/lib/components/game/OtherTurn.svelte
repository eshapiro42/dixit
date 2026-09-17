<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';

	let { view }: { view: SessionView } = $props();
	let selected = $state<string | null>(null);
	let submitting = $state(false);

	async function submit(): Promise<void> {
		if (!selected) return;
		submitting = true;
		await gameState.play(selected);
		submitting = false;
	}

	async function mulligan(): Promise<void> {
		if (!selected) return;
		await gameState.mulligan(selected);
		selected = null;
	}
</script>

{#if view.has_played}
	<section>
		<h2>Card played</h2>
		<p class="quiet">Waiting for the other players to choose.</p>
	</section>
{:else}
	<section>
		<h2>Match the prompt</h2>
		<p class="quiet">"{view.prompt}"</p>
		<CardRow
			cardIds={view.hand}
			selectable
			selectedId={selected}
			onselect={(id) => (selected = id)}
		/>
		<div class="actions">
			{#if view.mulligan_available}
				<Button kind="ghost" disabled={!selected} onclick={mulligan}>Mulligan</Button>
			{/if}
			<Button disabled={submitting || !selected} onclick={submit}>Play card</Button>
		</div>
	</section>
{/if}

<style>
	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
	}
</style>
