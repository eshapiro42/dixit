<script lang="ts">
	import type { Phase } from '../api/types';
	import { phaseSummary } from '../game/phase';
	import CopyChip from './CopyChip.svelte';
	import Text from './Text.svelte';

	interface Props {
		gameId: string;
		phase: Phase | null;
		host: string | null;
	}

	let { gameId, phase, host }: Props = $props();
</script>

<div class="status">
	<CopyChip value={gameId} label="Game ID" />
	{#key phase}
		<Text as="span" variant="label" class="phase">{phaseSummary(phase, host)}</Text>
	{/key}
</div>

<style>
	.status {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		min-width: 0;
	}

	.status :global(.phase) {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		animation: settle 0.2s ease;
	}

	@keyframes settle {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
	}
</style>
