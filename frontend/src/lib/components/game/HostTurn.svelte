<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import ConfirmDialog from '../ConfirmDialog.svelte';

	let { view }: { view: SessionView } = $props();

	let selected = $state<string | null>(null);
	let prompt = $state('');
	let submitting = $state(false);
	let confirmingMulligan = $state(false);

	// A solo-host round resolves entirely server-side, so this component never
	// remounts between rounds; clear a selection once its card leaves the hand.
	$effect(() => {
		if (selected !== null && !view.hand.includes(selected)) {
			selected = null;
			prompt = '';
		}
	});

	async function submit(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		if (!selected || !prompt.trim()) return;
		submitting = true;
		await gameState.hostChoice(selected, prompt.trim());
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

<section class="action-needed">
	<h2>Your Hand</h2>

	<CardRow
		cardIds={view.hand}
		selectable
		selectedId={selected}
		onselect={(id) => (selected = id)}
	/>

	<form onsubmit={submit}>
		<input type="text" bind:value={prompt} placeholder="Your prompt" maxlength="200" required />
		<div class="actions">
			{#if view.mulligan_available}
				<Button kind="ghost" disabled={!selected} onclick={askMulligan}>Mulligan</Button>
			{/if}
			<Button type="submit" disabled={submitting || !selected || !prompt.trim()}
				>Submit Choice</Button
			>
		</div>
	</form>
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
	form {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}

	input {
		min-height: var(--tap);
		padding: 0 var(--space-3);
		border-radius: var(--radius);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text);
		font: inherit;
	}

	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
	}
</style>
