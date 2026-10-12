<script lang="ts">
	import type { SessionView } from '../api/types';
	import { themeState } from '../game/theme.svelte';
	import Button from './Button.svelte';
	import GameStatus from './GameStatus.svelte';
	import Menu from './Menu.svelte';
	import MenuItem from './MenuItem.svelte';
	import ThemeToggle from './ThemeToggle.svelte';
	import Wordmark from './Wordmark.svelte';

	interface Props {
		view: SessionView | null;
		onOpenLog: () => void;
		onLeave: () => void;
	}

	let { view, onOpenLog, onLeave }: Props = $props();
</script>

<header class="topbar">
	<div class="inner">
		<Wordmark />
		{#if view}
			<GameStatus gameId={view.game_id} phase={view.phase} host={view.host} />
			<div class="actions">
				<Button kind="secondary" class="log-button" onclick={onOpenLog}>Game Log</Button>
				<Menu>
					<MenuItem icon="log" class="log-item" onclick={onOpenLog}>Game Log</MenuItem>
					<MenuItem
						icon={themeState.other === 'light' ? 'sun' : 'moon'}
						onclick={() => themeState.toggle()}
					>
						{themeState.other === 'light' ? 'Light' : 'Dark'} theme
					</MenuItem>
					<MenuItem icon="leave" tone="danger" onclick={onLeave}>Leave Game</MenuItem>
				</Menu>
			</div>
		{:else}
			<div class="actions">
				<ThemeToggle />
			</div>
		{/if}
	</div>
</header>

<style>
	.topbar {
		position: sticky;
		top: 0;
		z-index: var(--z-bar);
		background: var(--color-surface);
		border-bottom: var(--border-width) solid var(--color-border);
	}

	/* The status column shrinks and truncates, so the bar never wraps. */
	.inner {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto;
		align-items: center;
		column-gap: var(--space-3);
		height: var(--topbar-h);
		max-width: var(--page-max);
		margin: 0 auto;
		padding-inline: calc(var(--page-gutter) - var(--space-2)) var(--page-gutter);
	}

	.actions {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		grid-column: 3;
	}

	.actions :global(.log-button) {
		display: none;
	}

	@media (min-width: 48rem) {
		.actions :global(.log-button) {
			display: inline-flex;
		}

		.actions :global(.log-item) {
			display: none;
		}
	}

	/* Short landscape screens can't spare a sticky bar. */
	@media (max-height: 31.25rem) {
		.topbar {
			position: static;
		}
	}
</style>
