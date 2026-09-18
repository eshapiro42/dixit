<script lang="ts">
	import type { GameMessage } from '../api/types';
	import Button from './Button.svelte';

	interface Props {
		messages: GameMessage[];
	}

	interface Group {
		messages: GameMessage[];
		isRound: boolean;
		roundNumber: number;
	}

	let { messages }: Props = $props();
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
				current = { messages: [], isRound: message.round_start, roundNumber };
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
				{#if group.isRound}
					<button
						type="button"
						class="round-toggle"
						class:current={index === groups.length - 1}
						aria-expanded={isOpen(index)}
						onclick={() => toggle(index)}
					>
						<span class="chevron" class:open={isOpen(index)} aria-hidden="true">&#9656;</span>
						<span class="round-title">Round {group.roundNumber}</span>
						<span class="count numeric">{group.messages.length}</span>
					</button>
				{/if}
				{#if !group.isRound || isOpen(index)}
					<div class="messages">
						{#each group.messages as message, messageIndex (messageIndex)}
							<p class:emphasis={message.emphasis}>{message.text}</p>
						{/each}
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
		--icon-col: 1.25rem;
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
		font-size: var(--size-sm);
	}

	.messages {
		display: flex;
		flex-direction: column;
		gap: var(--space-1);
		padding-bottom: var(--space-1);
	}

	.round .messages {
		margin-left: var(--rule-x);
		padding-left: calc(var(--text-x) - var(--rule-x));
		border-left: 1px solid var(--color-border);
	}

	p {
		margin: 0;
		color: var(--color-text-quiet);
	}

	p.emphasis {
		color: var(--color-text);
		font-weight: 600;
	}

	.round-toggle {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		width: 100%;
		margin: 0;
		padding: var(--space-3) var(--space-2) var(--space-2);
		border: none;
		border-top: 1px solid var(--color-border);
		border-radius: var(--radius);
		background: none;
		font: inherit;
		font-weight: 500;
		color: var(--color-text-quiet);
		text-align: left;
		cursor: pointer;
	}

	.round-toggle:hover {
		background: var(--color-accent-soft);
	}

	.round-toggle.current {
		font-weight: 700;
		color: var(--color-text);
	}

	.chevron {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		width: var(--icon-col);
		font-size: var(--size-md);
		color: var(--color-accent);
		transition: transform 0.15s ease;
	}

	.chevron.open {
		transform: rotate(90deg);
	}

	.round-title {
		flex: 1 1 auto;
	}

	.count {
		flex-shrink: 0;
		min-width: 1.5em;
		padding: 0 var(--space-1);
		border-radius: var(--radius);
		background: var(--color-accent-soft);
		color: var(--color-text-quiet);
		font-size: var(--size-xs);
		font-weight: 600;
		text-align: center;
	}

	.jump-to-latest {
		position: absolute;
		bottom: var(--space-2);
		left: 50%;
		transform: translateX(-50%);
	}
</style>
