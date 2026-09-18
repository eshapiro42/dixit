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

{#key phase}
	<p class="label">{phaseLabel(phase, host, prompt)}</p>
{/key}

<style>
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
