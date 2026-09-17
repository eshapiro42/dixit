<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';

	let { view }: { view: SessionView } = $props();

	let selected = $state<string | null>(null);
	let prompt = $state('');
	let submitting = $state(false);

	async function submit(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		if (!selected || !prompt.trim()) return;
		submitting = true;
		await gameState.hostChoice(selected, prompt.trim());
		submitting = false;
	}

	async function mulligan(): Promise<void> {
		if (!selected) return;
		await gameState.mulligan(selected);
		selected = null;
	}
</script>

<section>
	<h2>Your turn to set the scene</h2>

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
				<Button kind="ghost" disabled={!selected} onclick={mulligan}>Mulligan</Button>
			{/if}
			<Button type="submit" disabled={submitting || !selected || !prompt.trim()}>Submit</Button>
		</div>
	</form>
</section>

<style>
	form {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}

	input {
		min-height: var(--tap);
		padding: 0 var(--space-3);
		border-radius: var(--radius-md);
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
