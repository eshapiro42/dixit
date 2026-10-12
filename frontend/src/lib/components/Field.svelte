<script lang="ts">
	import type { HTMLInputAttributes } from 'svelte/elements';
	import Text from './Text.svelte';

	interface Props extends Omit<HTMLInputAttributes, 'value' | 'id'> {
		id: string;
		label: string;
		value: string;
		hideLabel?: boolean;
	}

	let {
		id,
		label,
		value = $bindable(),
		hideLabel = false,
		required = false,
		class: className = '',
		...rest
	}: Props = $props();
</script>

<div class="field">
	<Text as="label" variant="label" for={id} class={hideLabel ? 'sr-only' : ''}>
		{label}
		{#if required && !hideLabel}<span class="required-marker" aria-hidden="true">*</span>{/if}
	</Text>
	<input {id} type="text" bind:value {required} autocomplete="off" class={className} {...rest} />
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
		border: var(--border-width) solid var(--color-border-strong);
		background: var(--color-surface);
		color: var(--color-text);
		font-family: inherit;
		font-size: var(--size-md);
		font-weight: var(--weight-normal);
	}
</style>
