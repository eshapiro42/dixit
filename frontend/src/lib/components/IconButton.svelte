<script lang="ts">
	interface Props {
		label: string;
		onclick: () => void;
		tone?: 'default' | 'danger';
	}

	let { label, onclick, tone = 'default' }: Props = $props();
</script>

<button type="button" class="icon-button {tone}" aria-label={label} {onclick}>&times;</button>

<style>
	.icon-button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: var(--tap);
		height: var(--tap);
		padding: 0;
		border: none;
		border-radius: var(--radius);
		background: none;
		color: var(--color-text-quiet);
		font-size: var(--size-xl);
		line-height: 1;
		cursor: pointer;
		transition:
			background-color 0.15s ease,
			color 0.15s ease;
	}

	.icon-button:hover {
		background: var(--color-accent-soft);
		color: var(--color-text);
	}

	.icon-button.danger {
		color: var(--color-danger);
	}

	.icon-button.danger:hover {
		background: var(--color-danger-soft);
	}
</style>
