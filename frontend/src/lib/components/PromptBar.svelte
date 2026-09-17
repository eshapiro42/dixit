<script lang="ts">
	import type { Phase } from '../api/types';
	import { phaseLabel } from '../game/phase';

	interface Props {
		phase: Phase | null;
		host: string | null;
		prompt: string | null;
	}

	let { phase, host, prompt }: Props = $props();
</script>

<div class="bar">
	{#key phase}
		<p class="label">{phaseLabel(phase, host, prompt)}</p>
	{/key}
</div>

<style>
	.bar {
		border-bottom: 1px solid var(--color-border);
		padding-bottom: var(--space-3);
		margin-bottom: var(--space-4);
	}

	.label {
		margin: 0;
		font-weight: 600;
		animation: settle 0.2s ease;
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
</style>
