<script lang="ts">
	import type { HTMLButtonAttributes } from 'svelte/elements';
	import Icon, { type IconName } from './Icon.svelte';

	interface Props extends HTMLButtonAttributes {
		icon: IconName;
		label: string;
		tone?: 'default' | 'danger';
	}

	let { icon, label, tone = 'default', class: className = '', ...rest }: Props = $props();
</script>

<button type="button" class="icon-button {tone} {className}" aria-label={label} {...rest}>
	<Icon name={icon} />
</button>

<style>
	.icon-button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		width: var(--tap);
		height: var(--tap);
		padding: 0;
		border: none;
		border-radius: var(--radius);
		background: none;
		color: var(--color-text-quiet);
		cursor: pointer;
		transition:
			background-color 0.15s ease,
			color 0.15s ease;
	}

	@media (hover: hover) {
		.icon-button:hover {
			background: var(--color-accent-soft);
			color: var(--color-text);
		}

		.icon-button.danger:hover {
			background: var(--color-danger-soft);
		}
	}

	.icon-button:active {
		background: var(--color-accent-soft);
	}

	.icon-button.danger {
		color: var(--color-danger);
	}

	.icon-button.danger:active {
		background: var(--color-danger-soft);
	}
</style>
