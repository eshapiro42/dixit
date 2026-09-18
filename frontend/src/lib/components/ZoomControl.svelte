<script lang="ts">
	import { zoomState } from '../game/zoom.svelte';

	const zoomId = $props.id();
</script>

<div class="zoom-control">
	<label for={zoomId}>Zoom</label>
	<input id={zoomId} type="range" min="0.6" max="2" step="0.1" bind:value={zoomState.value} />
</div>

<style>
	.zoom-control {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		font-size: var(--size-xs);
		color: var(--color-text-quiet);
	}

	.zoom-control input {
		width: 100px;
	}
</style>
