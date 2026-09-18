<script lang="ts">
	import type { SessionView } from '../api/types';
	import { phaseLabel } from '../game/phase';
	import Button from './Button.svelte';
	import ZoomControl from './ZoomControl.svelte';

	interface Props {
		view: SessionView | null;
		onOpenLog: () => void;
		onLeave: () => void;
	}

	let { view, onOpenLog, onLeave }: Props = $props();
</script>

<header class="topbar">
	<div class="inner">
		<h1 class="wordmark">Dixit</h1>
		{#if view}
			{#key view.phase}
				<p class="status">{phaseLabel(view.phase, view.host, view.prompt)}</p>
			{/key}
			<div class="meta">
				<span class="quiet numeric">Game ID: {view.game_id}</span>
				{#if view.started}
					<ZoomControl />
				{/if}
				<Button kind="secondary" onclick={onOpenLog}>Game Log</Button>
				<Button kind="ghost" onclick={onLeave}>Leave Game</Button>
			</div>
		{/if}
	</div>
</header>

<style>
	.topbar {
		position: sticky;
		top: 0;
		z-index: 20;
		background: var(--color-surface-sunken);
		border-bottom: 1px solid var(--color-border);
	}

	.inner {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: var(--space-2) var(--space-4);
		max-width: 1400px;
		margin: 0 auto;
		padding: var(--space-3) var(--space-4);
	}

	.wordmark {
		flex-shrink: 0;
		font-size: var(--size-md);
	}

	.status {
		flex: 1 1 auto;
		min-width: 0;
		margin: 0;
		font-weight: 600;
		animation: settle 0.2s ease;
	}

	.meta {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		flex-shrink: 0;
		margin-left: auto;
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
		.status {
			animation: none;
		}
	}
</style>
