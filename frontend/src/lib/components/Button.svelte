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
		border-radius: var(--radius-md);
		border: 1px solid transparent;
		font-family: inherit;
		font-size: var(--size-sm);
		font-weight: 600;
		text-decoration: none;
		cursor: pointer;
		transition:
			background-color 0.15s ease,
			border-color 0.15s ease,
			opacity 0.15s ease;
	}

	.button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.primary {
		background: var(--color-accent);
		color: var(--color-accent-contrast);
	}

	.primary:not(:disabled):hover {
		filter: brightness(1.08);
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
		color: white;
	}

	.ghost {
		background: transparent;
		color: var(--color-text-quiet);
	}

	.ghost:not(:disabled):hover {
		color: var(--color-text);
	}
</style>
