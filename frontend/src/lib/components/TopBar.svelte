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
					<!-- eslint-disable-next-line svelte/no-useless-mustaches -- keeps the trailing space prettier would strip -->
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

	/* Baseline alignment is scoped to .status-line so the pair centers in the bar as a unit. */
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
		/* Cancels .inner's column-gap here so the dot gets the same space on both sides. */
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
		/* Matches .game-id's gap so both dots are centered between their neighbors. */
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
		/* Must match .wordmark-wrap's right padding so the dot is centered. */
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

	/* Without the buttons the bar would be shorter on the create/join screen. */
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
