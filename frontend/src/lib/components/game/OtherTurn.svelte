<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import ConfirmDialog from '../ConfirmDialog.svelte';
	import PanelHeader from '../PanelHeader.svelte';
	import PromptCaption from '../PromptCaption.svelte';
	import Text from '../Text.svelte';
	import ZoomControl from '../ZoomControl.svelte';

	let { view }: { view: SessionView } = $props();
	let selected = $state<string | null>(null);
	let submitting = $state(false);
	let confirmingMulligan = $state(false);

	let canPlay = $derived(!view.has_played);

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

<section class:action-needed={canPlay}>
	<PanelHeader>
		<Text variant="heading">Your Hand</Text>
		<ZoomControl kind="hand" />
	</PanelHeader>
	{#if view.host && view.prompt}
		<PromptCaption host={view.host} prompt={view.prompt} />
	{/if}
	<CardRow
		kind="hand"
		cardIds={view.hand}
		selectable={canPlay}
		selectedId={selected}
		onselect={(id) => (selected = selected === id ? null : id)}
	/>
	{#if canPlay}
		<div class="actions">
			<Button disabled={submitting || !selected} onclick={submit}>Submit</Button>
			{#if view.mulligan_available}
				<Button kind="ghost" disabled={!selected} onclick={askMulligan}>Mulligan</Button>
			{/if}
		</div>
	{/if}
</section>

<ConfirmDialog
	open={confirmingMulligan}
	title="Mulligan"
	message="This will discard the selected card and draw a replacement."
	confirmLabel="Mulligan"
	onconfirm={confirmMulligan}
	oncancel={() => (confirmingMulligan = false)}
/>

<style>
	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
	}

	.actions :global(.ghost) {
		margin-left: auto;
	}
</style>
