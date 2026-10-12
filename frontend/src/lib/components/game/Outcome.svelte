<script lang="ts">
	import type { RoundOutcome } from '../../api/types';
	import CardRow from '../CardRow.svelte';
	import Divider from '../Divider.svelte';
	import Text from '../Text.svelte';
	import GamePanel from './GamePanel.svelte';

	let { outcome }: { outcome: RoundOutcome } = $props();

	let cardIds = $derived(Object.values(outcome.table));
	let labels = $derived(
		Object.fromEntries(Object.entries(outcome.table).map(([name, cardId]) => [cardId, name]))
	);
	let votes = $derived.by(() => {
		const byCard: Record<string, string[]> = {};
		for (const [voter, cardId] of Object.entries(outcome.votes)) {
			(byCard[cardId] ??= []).push(voter);
		}
		return byCard;
	});

	let zeroRuleMessage = $derived(
		outcome.correct_voter_count === 0
			? `No one matched ${outcome.host}'s card, so ${outcome.host} scored 0 this round.`
			: `Everyone matched ${outcome.host}'s card, so ${outcome.host} scored 0 this round.`
	);

	const ZERO_RULE_SEEN_KEY = 'dixit:seen-zero-rule';
	let showZeroRuleExplainer = $state(false);

	$effect(() => {
		if (outcome.scores[outcome.host] !== 0) {
			showZeroRuleExplainer = false;
			return;
		}
		let alreadySeen = false;
		try {
			alreadySeen = localStorage.getItem(ZERO_RULE_SEEN_KEY) === '1';
			if (!alreadySeen) localStorage.setItem(ZERO_RULE_SEEN_KEY, '1');
		} catch {
			// Best-effort only: a private window or blocked storage just shows it every time.
		}
		showZeroRuleExplainer = !alreadySeen;
	});
</script>

<Divider spacing="section" />
<GamePanel
	title="Round {outcome.round_number} Results"
	zoomKind="table"
	prompt={{ host: outcome.host, text: outcome.prompt }}
>
	{#if showZeroRuleExplainer}
		<Text as="p" variant="caption" class="callout">{zeroRuleMessage}</Text>
	{/if}
	<CardRow kind="table" {cardIds} {labels} {votes} />
</GamePanel>

<style>
	:global(.callout) {
		max-width: 40em;
	}
</style>
