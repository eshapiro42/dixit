<script lang="ts">
	interface Props {
		id: string;
		label: string;
		value: string;
		required?: boolean;
		maxlength?: number;
		placeholder?: string;
	}

	let {
		id,
		label,
		value = $bindable(),
		required = false,
		maxlength,
		placeholder
	}: Props = $props();
</script>

<div class="field">
	<label for={id}>
		{label}
		{#if required}<span aria-hidden="true">*</span>{/if}
	</label>
	<input {id} type="text" bind:value {required} {maxlength} {placeholder} autocomplete="off" />
</div>

<style>
	.field {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	label {
		font-size: var(--size-sm);
		font-weight: 600;
		color: var(--color-text-quiet);
	}

	label span {
		color: var(--color-danger);
	}

	input {
		min-height: var(--tap);
		padding: 0 var(--space-3);
		border-radius: var(--radius);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text);
		font-family: inherit;
		font-size: var(--size-md);
	}

	input:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: 1px;
	}
</style>
