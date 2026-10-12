<script lang="ts">
	import type { SessionView } from '../api/types';
	import { phaseLabel } from '../game/phase';
	import BunnyIcon from './BunnyIcon.svelte';
	import Button from './Button.svelte';
	import Text from './Text.svelte';
	import ThemeToggle from './ThemeToggle.svelte';

	interface Props {
		view: SessionView | null;
		onOpenLog: () => void;
		onLeave: () => void;
	}

	let { view, onOpenLog, onLeave }: Props = $props();
</script>

<header class="topbar">
	<div class="inner">
		<span class="wordmark-wrap">
			<BunnyIcon class="bunny-behind" />
			<Text variant="title" class="wordmark">Dixit</Text>
		</span>
		{#if view}
			<span class="status-line">
				<span class="game-id">
					<span class="dot" aria-hidden="true">&middot;</span>
					<Text as="span" variant="label" class="sr-only">{'Game ID: '}</Text>
					<Text as="span" variant="label" class="numeric">{view.game_id}</Text>
				</span>
				<span class="dot" aria-hidden="true">&middot;</span>
				{#key view.phase}
					<Text as="p" variant="label" class="status">{phaseLabel(view.phase, view.host)}</Text>
				{/key}
			</span>
			<div class="meta">
				<ThemeToggle />
				<Button kind="secondary" onclick={onOpenLog}>Game Log</Button>
				<Button kind="ghost" onclick={onLeave}>Leave Game</Button>
			</div>
		{:else}
			<div class="meta meta--solo">
				<ThemeToggle />
			</div>
		{/if}
	</div>
</header>

<style>
	.topbar {
		position: sticky;
		top: 0;
		z-index: 20;
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-border);
	}

	/* Every direct child is centered as a block against the tallest one (the
	 * buttons, at --tap height) so the bar reads as vertically balanced. The
	 * game ID and status text still need to share a baseline with EACH OTHER
	 * the way running text would, but comparing baselines across the whole
	 * row - including a 44px-tall button - would just shove that pair up
	 * near the top of the bar instead of centering them in it. Scoping
	 * align-items: baseline to their own wrapper (.status-line) gets both:
	 * the pair lines up with each other, and the pair as a unit still
	 * centers in the bar like everything else. */
	.inner {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: var(--space-2) var(--space-4);
		max-width: 1400px;
		margin: 0 auto;
		padding: var(--space-3) var(--space-4);
	}

	.wordmark-wrap {
		position: relative;
		display: inline-flex;
		align-items: center;
		flex-shrink: 0;
		padding: 0 var(--space-2);
		/* .inner's own column-gap lands between every pair of its direct
		 * children, including this one and .status-line - on top of the
		 * padding above, which would double the space before the dot vs.
		 * after it. Cancel that one contribution so the padding above stays
		 * the sole source of that gap, keeping it equal to .game-id's own
		 * internal gap on the dot's other side. */
		margin-right: calc(-1 * var(--space-4));
	}

	.wordmark-wrap :global(.bunny-behind) {
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		height: 3.4em;
		width: auto;
		fill: var(--color-accent);
		opacity: var(--opacity-faded);
		z-index: 0;
		pointer-events: none;
	}

	.wordmark-wrap :global(.wordmark) {
		position: relative;
		z-index: 1;
	}

	.status-line {
		display: inline-flex;
		align-items: baseline;
		flex: 1 1 auto;
		min-width: 0;
		/* Same token as .game-id's own internal gap below, so the dot between
		 * the game ID and the status text sits centered exactly like the one
		 * between "Dixit" and the game ID does. */
		gap: var(--space-2);
	}

	.status-line > .dot {
		flex-shrink: 0;
	}

	.game-id {
		position: relative;
		z-index: 1;
		display: inline-flex;
		align-items: baseline;
		flex-shrink: 0;
		/* .wordmark-wrap's own right padding is the gap before the dot; this
		 * gap after it needs to match that same token so the dot actually
		 * sits centered between "Dixit" and the code instead of hugging
		 * whichever side happens to get the leftover margin. */
		gap: var(--space-2);
	}

	.status-line .dot {
		color: var(--color-text-quiet);
	}

	.status-line > :global(.status) {
		flex: 1 1 auto;
		min-width: 0;
		animation: settle 0.2s ease;
	}

	.meta {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		flex-shrink: 0;
		margin-left: auto;
	}

	.meta > :global(*) {
		white-space: nowrap;
	}

	/* In-game, the buttons (--tap tall) set the bar's height; without a game
	 * there are none, so the wordmark alone would leave the bar shorter on the
	 * create/join screen. Matching its minimum to the buttons keeps the bar one
	 * height throughout. (On narrow screens the buttons wrap to their own row,
	 * so there's nothing to match.) */
	@media (min-width: 481px) {
		.wordmark-wrap {
			min-height: var(--tap);
		}
	}

	@media (max-width: 480px) {
		.inner {
			padding: var(--space-2) var(--space-3);
		}

		.meta {
			flex-basis: 100%;
			flex-wrap: wrap;
			margin-left: 0;
			justify-content: flex-start;
		}

		/* Just the theme toggle (no game yet): nothing to wrap onto its own row. */
		.meta--solo {
			flex-basis: auto;
			margin-left: auto;
		}
	}

	@keyframes settle {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.status-line > :global(.status) {
			animation: none;
		}
	}
</style>
