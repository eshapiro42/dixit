<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { gameState } from '../../game/state.svelte';
	import Button from '../Button.svelte';
	import CardRow from '../CardRow.svelte';
	import PanelHeader from '../PanelHeader.svelte';
	import PromptCaption from '../PromptCaption.svelte';
	import Text from '../Text.svelte';
	import ZoomControl from '../ZoomControl.svelte';

	let { view }: { view: SessionView } = $props();
	let selected = $state<string | null>(null);
	let submitting = $state(false);

	let isHost = $derived(view.host === view.player_name);
	let canVote = $derived(!isHost && !view.has_voted);

	async function submit(): Promise<void> {
		if (!selected) return;
		submitting = true;
		await gameState.vote(selected);
		submitting = false;
	}
</script>

<section class:action-needed={canVote}>
	<PanelHeader>
		<Text variant="heading">Table</Text>
		<ZoomControl kind="table" />
	</PanelHeader>
	{#if view.host && view.prompt}
		<PromptCaption host={view.host} prompt={view.prompt} />
	{/if}
	<CardRow
		kind="table"
		cardIds={view.table ?? []}
		selectable={canVote}
		selectedId={selected}
		onselect={(id) => (selected = selected === id ? null : id)}
	/>
	{#if canVote}
		<Button disabled={submitting || !selected} onclick={submit}>Submit Vote</Button>
	{/if}
</section>
