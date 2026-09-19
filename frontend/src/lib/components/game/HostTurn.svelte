<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import ConfirmDialog from '../ConfirmDialog.svelte';
	import PanelHeader from '../PanelHeader.svelte';
	import Text from '../Text.svelte';
	import ZoomControl from '../ZoomControl.svelte';

	let { view }: { view: SessionView } = $props();

	const promptId = $props.id();

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
	<PanelHeader>
		<Text variant="heading">Your Hand</Text>
		<ZoomControl kind="hand" />
	</PanelHeader>

	<CardRow
		kind="hand"
		cardIds={view.hand}
		selectable
		selectedId={selected}
		onselect={(id) => (selected = selected === id ? null : id)}
	/>

	<form onsubmit={submit}>
		<Text as="label" variant="label" for={promptId} class="sr-only">Your prompt</Text>
		<input
			id={promptId}
			type="text"
			bind:value={prompt}
			placeholder="Your prompt"
			maxlength="200"
			required
		/>
		<div class="actions">
			<Button type="submit" disabled={submitting || !selected || !prompt.trim()}
				>Submit</Button
			>
			{#if view.mulligan_available}
				<Button kind="ghost" disabled={!selected} onclick={askMulligan}>Mulligan</Button>
			{/if}
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
		padding: 0 var(--space-4);
		border-radius: var(--radius);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text);
		font: inherit;
	}

	input:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: 1px;
	}

	.actions {
		display: flex;
		gap: var(--space-3);
		flex-wrap: wrap;
	}

	.actions :global(.ghost) {
		margin-left: auto;
	}
</style>
