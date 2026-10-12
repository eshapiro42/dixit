<script lang="ts">
	import type { GameMessage, RoundOutcome } from '../api/types';
	import Badge from './Badge.svelte';
	import Button from './Button.svelte';
	import RoundResultStrip from './RoundResultStrip.svelte';
	import Text from './Text.svelte';

	interface Props {
		messages: GameMessage[];
		outcomes?: RoundOutcome[];
		open: boolean;
	}

	interface Group {
		messages: GameMessage[];
		isRound: boolean;
		roundNumber: number;
		outcome: RoundOutcome | undefined;
	}

	let { messages, outcomes = [], open }: Props = $props();
	let listEl: HTMLElement | undefined;
	// Only follow new messages while already reading the bottom of the log;
	// once the user scrolls up to read history, leave them where they are.
	let stickToBottom = $state(true);
	// Which round groups the user has manually toggled, overriding the default
	// (every past round collapsed, the round in progress expanded).
	let openOverrides = $state<Record<number, boolean>>({});

	function trackScrollPosition(): void {
		if (!listEl) return;
		const distanceFromBottom = listEl.scrollHeight - listEl.scrollTop - listEl.clientHeight;
		stickToBottom = distanceFromBottom < 16;
	}

	function jumpToLatest(): void {
		stickToBottom = true;
		listEl?.scrollTo({ top: listEl.scrollHeight, behavior: 'smooth' });
	}

	$effect(() => {
		const count = messages.length;
		if (count > 0 && stickToBottom) listEl?.scrollTo({ top: listEl.scrollHeight });
	});

	// While the dialog is closed the log sits under display:none, where a
	// scrollTo() call has nothing real to measure against and quietly does
	// nothing — so history that arrives while it's closed leaves scrollTop
	// stale. Re-snap once it's actually visible and laid out again.
	$effect(() => {
		if (!open || !stickToBottom) return;
		requestAnimationFrame(() => listEl?.scrollTo({ top: listEl.scrollHeight }));
	});

	// Messages before the first "it's your turn" announcement (room created,
	// players joining, game started) are one always-visible group; each round
	// after that becomes its own collapsible group.
	let groups = $derived.by((): Group[] => {
		const result: Group[] = [];
		let current: Group | null = null;
		let roundNumber = 0;
		for (const message of messages) {
			if (message.round_start || !current) {
				if (message.round_start) roundNumber += 1;
				current = {
					messages: [],
					isRound: message.round_start,
					roundNumber,
					outcome: message.round_start
						? outcomes.find((o) => o.round_number === roundNumber)
						: undefined
				};
				result.push(current);
			}
			current.messages.push(message);
		}
		return result;
	});

	function isOpen(index: number): boolean {
		return openOverrides[index] ?? index === groups.length - 1;
	}

	function toggle(index: number): void {
		openOverrides = { ...openOverrides, [index]: !isOpen(index) };
	}
</script>

<div class="log-wrapper">
	<div class="log" bind:this={listEl} onscroll={trackScrollPosition}>
		{#each groups as group, index (index)}
			<section class="group" class:round={group.isRound}>
				{#if !group.isRound}
					<h3 class="group-title">Lobby</h3>
				{:else}
					<button
						type="button"
						class="round-toggle"
						class:current={index === groups.length - 1}
						aria-expanded={isOpen(index)}
						onclick={() => toggle(index)}
					>
						<svg class="chevron" class:open={isOpen(index)} viewBox="0 0 16 16" aria-hidden="true">
							<path d="M6 4l4 4-4 4" />
						</svg>
						<span class="round-heading">
							<span class="round-title">Round {group.roundNumber}</span>
							{#if group.outcome && !isOpen(index)}
								<span class="round-summary">
									{group.outcome.host}'s prompt: &ldquo;{group.outcome.prompt}&rdquo;
								</span>
							{/if}
						</span>
						<Badge tone="soft" class="count">{group.messages.length}</Badge>
					</button>
				{/if}
				{#if !group.isRound || isOpen(index)}
					<div class="messages">
						{#each group.messages as message, messageIndex (messageIndex)}
							{#if message.emphasis}
								<Text as="p" variant="body" class="log-emphasis">{message.text}</Text>
							{:else}
								<Text as="p" variant="caption">{message.text}</Text>
							{/if}
						{/each}
						{#if group.outcome}
							<div class="results">
								<Text as="span" variant="tag">Results</Text>
								<RoundResultStrip outcome={group.outcome} />
							</div>
						{/if}
					</div>
				{/if}
			</section>
		{/each}
	</div>
	{#if !stickToBottom && messages.length > 0}
		<div class="jump-to-latest">
			<Button kind="secondary" onclick={jumpToLatest}>&darr; Jump to latest</Button>
		</div>
	{/if}
</div>

<style>
	/* A flex item of Dialog's .content, which is itself a bounded-height flex
	 * column: min-height: 0 is what lets this actually shrink to fit instead
	 * of growing to its content's full height, so .log below gets a real
	 * boundary to scroll within instead of leaving that to .content.
	 */
	.log-wrapper {
		position: relative;
		display: flex;
		flex-direction: column;
		flex: 1 1 auto;
		min-height: 0;
	}

	.log {
		--icon-col: var(--size-lg);
		/* Where the round's connecting rule sits: under the chevron's center. */
		--rule-x: calc(var(--space-2) + var(--icon-col) / 2);
		/* Where message text sits: clearly past the round title's own indent
		 * (button padding + icon column + its gap to the title), so a round's
		 * messages always read as nested deeper than the "Round N" heading. */
		--text-x: calc(var(--space-2) + var(--icon-col) + var(--space-2) + var(--space-3));

		display: flex;
		flex-direction: column;
		flex: 1 1 auto;
		min-height: 0;
		overflow-y: auto;
	}

	.messages {
		position: relative;
		display: flex;
		flex-direction: column;
		gap: var(--space-1);
		padding-bottom: var(--space-1);
	}

	.round .messages {
		margin-left: var(--rule-x);
		padding-left: calc(var(--text-x) - var(--rule-x));
	}

	/* A pseudo-element instead of a plain border-left: a border always spans
	 * the full box, right down to where the next round's divider begins,
	 * which reads as the two lines crossing. Insetting the bottom leaves a
	 * gap between them instead.
	 */
	.round .messages::before {
		content: '';
		position: absolute;
		top: 0;
		bottom: var(--space-2);
		left: 0;
		width: 1px;
		background: var(--color-accent-soft);
	}

	.messages :global(.log-emphasis) {
		font-weight: var(--weight-medium);
	}

	.round-toggle {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		width: 100%;
		margin: 0;
		padding: var(--space-3) var(--space-2) var(--space-2);
		border: none;
		border-top: var(--border-width) solid var(--color-border);
		border-radius: var(--radius);
		background: none;
		font-family: inherit;
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		color: var(--color-text-quiet);
		text-align: left;
		cursor: pointer;
	}

	.round-toggle:hover {
		background: var(--color-accent-soft);
	}

	.round-toggle.current {
		font-weight: var(--weight-bold);
		color: var(--color-text);
	}

	/* An SVG (not a glyph) so the tip is exactly centered by construction:
	 * it's vertically centered in the viewBox, so rotating the box 90° around
	 * its own center always lands the tip exactly on the box's horizontal
	 * center — which is where .round .messages positions the rule below it.
	 */
	.chevron {
		flex-shrink: 0;
		width: var(--icon-col);
		height: var(--icon-col);
		transition: transform 0.15s ease;
	}

	.chevron path {
		fill: none;
		stroke: var(--color-accent);
		stroke-width: 2;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	.chevron.open {
		transform: rotate(90deg);
	}

	.round-heading {
		display: flex;
		flex-direction: column;
		flex: 1 1 auto;
		min-width: 0;
		gap: 2px;
	}

	.round-title {
		line-height: 1.3;
	}

	.round-summary {
		overflow: hidden;
		font-size: var(--size-xs);
		font-weight: var(--weight-normal);
		color: var(--color-text-quiet);
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.group-title {
		margin: 0;
		padding: var(--space-2) 0;
		font-family: var(--font-sans);
		font-size: var(--size-sm);
		font-weight: var(--weight-bold);
		color: var(--color-text);
	}

	.results {
		display: flex;
		flex-direction: column;
		gap: var(--space-1);
		margin-top: var(--space-2);
		padding-top: var(--space-2);
		border-top: var(--border-width) dashed var(--color-border);
	}

	.round-toggle :global(.count) {
		flex-shrink: 0;
		min-width: 1.5em;
		color: var(--color-text-quiet);
		font-size: var(--size-xs);
		text-align: center;
	}

	.jump-to-latest {
		position: absolute;
		bottom: var(--space-2);
		left: 50%;
		transform: translateX(-50%);
	}
</style>
