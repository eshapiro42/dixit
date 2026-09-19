<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		kind?: 'primary' | 'secondary' | 'danger' | 'ghost';
		type?: 'button' | 'submit';
		disabled?: boolean;
		onclick?: (event: MouseEvent) => void;
		children: Snippet;
	}

	let { kind = 'primary', type = 'button', disabled = false, onclick, children }: Props = $props();
</script>

<button class="button {kind}" {type} {disabled} {onclick}>
	{@render children()}
</button>

<style>
	.button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-2);
		min-height: var(--tap);
		padding: 0 var(--space-4);
		border-radius: var(--radius);
		border: 1px solid transparent;
		font-family: inherit;
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		text-decoration: none;
		cursor: pointer;
		/* The button's own height comes from min-height, not the label's line
		 * box, so trimming that line box to the label's actual glyph metrics
		 * only affects how it's centered within the button - not the
		 * button's size - making that centering line up with other
		 * geometrically-centered elements (e.g. the zoom slider's track)
		 * regardless of which font a given browser substitutes in.
		 */
		text-box-trim: trim-both;
		text-box-edge: cap alphabetic;
		transition:
			background-color 0.15s ease,
			border-color 0.15s ease,
			opacity 0.15s ease;
	}

	.button:disabled {
		opacity: var(--opacity-faded);
		cursor: not-allowed;
	}

	.primary {
		background: var(--color-accent);
		color: var(--color-accent-contrast);
	}

	.primary:not(:disabled):hover {
		filter: brightness(0.94);
	}

	.secondary {
		background: var(--color-surface);
		border-color: var(--color-border);
		color: var(--color-text);
	}

	.secondary:not(:disabled):hover {
		border-color: var(--color-accent);
	}

	.danger {
		background: var(--color-danger);
		color: var(--color-danger-contrast);
	}

	.ghost {
		background: transparent;
		border-color: var(--color-border);
		color: var(--color-text-quiet);
	}

	.ghost:not(:disabled):hover {
		border-color: var(--color-accent);
		color: var(--color-text);
	}
</style>
