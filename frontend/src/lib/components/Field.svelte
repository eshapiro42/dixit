<script lang="ts">
	import Text from './Text.svelte';

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
	<Text as="label" variant="label" for={id}>
		{label}
		{#if required}<span class="required-marker" aria-hidden="true">*</span>{/if}
	</Text>
	<input {id} type="text" bind:value {required} {maxlength} {placeholder} autocomplete="off" />
</div>

<style>
	.field {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.required-marker {
		color: var(--color-danger);
	}

	input {
		min-height: var(--tap);
		padding: 0 var(--space-4);
		border-radius: var(--radius);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text);
		font-family: inherit;
		font-size: var(--size-md);
		font-weight: var(--weight-normal);
	}

	input:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: 1px;
	}
</style>
