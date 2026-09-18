<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import Clue from '../Clue.svelte';
	import ConfirmDialog from '../ConfirmDialog.svelte';
	import Waiting from '../Waiting.svelte';

	let { view }: { view: SessionView } = $props();
	let selected = $state<string | null>(null);
	let submitting = $state(false);
	let confirmingMulligan = $state(false);

	// Clears a selection once its card leaves the hand, so a card played (and
	// discarded) last round can't linger as an enabled-but-invalid selection.
	$effect(() => {
		if (selected !== null && !view.hand.includes(selected)) {
			selected = null;
		}
	});

	async function submit(): Promise<void> {
		if (!selected) return;
		submitting = true;
		await gameState.play(selected);
		submitting = false;
	}

	function askMulligan(): void {
		if (!selected) return;
		confirmingMulligan = true;
	}

	async function confirmMulligan(): Promise<void> {
		confirmingMulligan = false;
		if (!selected) return;
		await gameState.mulligan(selected);
		selected = null;
	}
</script>

{#if view.has_played}
	<Waiting detail="Waiting for the other players to choose." />
{:else}
	<section class="action-needed">
		{#if view.host && view.prompt}
			<Clue host={view.host} prompt={view.prompt} />
		{/if}
		<h2>Your Hand</h2>
		<CardRow
			cardIds={view.hand}
			selectable
			selectedId={selected}
			onselect={(id) => (selected = id)}
		/>
		<div class="actions">
			{#if view.mulligan_available}
				<Button kind="ghost" disabled={!selected} onclick={askMulligan}>Mulligan</Button>
			{/if}
			<Button disabled={submitting || !selected} onclick={submit}>Submit Choice</Button>
		</div>
	</section>

	<ConfirmDialog
		open={confirmingMulligan}
		title="Mulligan"
		message="This will discard the selected card and draw a replacement."
		confirmLabel="Mulligan"
		onconfirm={confirmMulligan}
		oncancel={() => (confirmingMulligan = false)}
	/>
{/if}

<style>
	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
	}
</style>
