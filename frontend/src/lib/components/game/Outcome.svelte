<script lang="ts">
	import type { PlayerSummary, RoundOutcome } from '../../api/types';
	import CardRow from '../CardRow.svelte';
	import Divider from '../Divider.svelte';
	import PanelHeader from '../PanelHeader.svelte';
	import PromptCaption from '../PromptCaption.svelte';
	import Text from '../Text.svelte';
	import ZoomControl from '../ZoomControl.svelte';

	let { outcome, players }: { outcome: RoundOutcome; players: PlayerSummary[] } = $props();

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
	// CPUs never compete for score, so they get no delta badge at all.
	let cpuNames = $derived(new Set(players.filter((p) => p.is_cpu).map((p) => p.name)));
	let deltas = $derived.by(() => {
		const byCard: Record<string, number> = {};
		for (const [name, cardId] of Object.entries(outcome.table)) {
			if (cpuNames.has(name)) continue;
			byCard[cardId] = outcome.scores[name] ?? 0;
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
<section>
	<PanelHeader>
		<Text variant="heading">Round {outcome.round_number} Results</Text>
		<ZoomControl kind="results" />
	</PanelHeader>
	<PromptCaption host={outcome.host} prompt={outcome.prompt} />
	{#if showZeroRuleExplainer}
		<Text as="p" variant="caption" class="callout">{zeroRuleMessage}</Text>
	{/if}
	<CardRow kind="results" {cardIds} {labels} {votes} {deltas} />
</section>

<style>
	:global(.callout) {
		max-width: 40em;
	}
</style>
