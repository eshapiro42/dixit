<script lang="ts">
	import { ClipboardFeedback } from '../game/clipboard.svelte';
	import Icon from './Icon.svelte';

	let { value, label }: { value: string; label: string } = $props();

	const clipboard = new ClipboardFeedback();
</script>

<button
	type="button"
	class="chip"
	aria-label="{label}: {value}. Copy"
	onclick={() => clipboard.copy(value)}
>
	<span class="value numeric">{value}</span>
	<Icon name={clipboard.copied ? 'check' : 'copy'} size={14} />
</button>
<span class="sr-only" role="status">
	{clipboard.copied ? `${label} copied` : clipboard.failed ? "Couldn't copy" : ''}
</span>

<style>
	.chip {
		position: relative;
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		min-height: 2rem;
		padding: 0 var(--space-2);
		border: var(--border-width) solid var(--color-border-strong);
		border-radius: var(--radius);
		background: none;
		color: var(--color-text);
		font-family: var(--font-mono);
		font-size: var(--size-sm);
		font-weight: var(--weight-bold);
		letter-spacing: 0.05em;
		cursor: pointer;
	}

	/* Keeps the chip compact while the touch target stays full size. */
	.chip::before {
		content: '';
		position: absolute;
		inset: calc((2rem - var(--tap)) / 2) 0;
	}

	@media (hover: hover) {
		.chip:hover {
			background: var(--color-accent-soft);
		}
	}

	.chip:active {
		background: var(--color-accent-soft);
	}
</style>
