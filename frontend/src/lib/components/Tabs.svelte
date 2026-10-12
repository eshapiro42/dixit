<script lang="ts" generics="T extends string">
	import type { Snippet } from 'svelte';

	interface Props {
		tabs: { id: T; label: string }[];
		value: T;
		label: string;
		onchange?: (id: T) => void;
		children: Snippet;
	}

	let { tabs, value = $bindable(), label, onchange, children }: Props = $props();

	const uid = $props.id();
	const tabId = (id: T) => `${uid}-tab-${id}`;
	const panelId = `${uid}-panel`;

	function select(id: T): void {
		if (id === value) return;
		value = id;
		onchange?.(id);
	}

	function onkeydown(event: KeyboardEvent): void {
		const index = tabs.findIndex((tab) => tab.id === value);
		const target =
			event.key === 'ArrowRight'
				? (index + 1) % tabs.length
				: event.key === 'ArrowLeft'
					? (index - 1 + tabs.length) % tabs.length
					: event.key === 'Home'
						? 0
						: event.key === 'End'
							? tabs.length - 1
							: null;
		if (target === null) return;
		event.preventDefault();
		select(tabs[target].id);
		document.getElementById(tabId(tabs[target].id))?.focus();
	}
</script>

<div class="tabs" role="tablist" aria-label={label} {onkeydown} tabindex="-1">
	{#each tabs as tab (tab.id)}
		<button
			type="button"
			role="tab"
			id={tabId(tab.id)}
			class="tab"
			aria-selected={value === tab.id}
			aria-controls={panelId}
			tabindex={value === tab.id ? 0 : -1}
			onclick={() => select(tab.id)}
		>
			{tab.label}
		</button>
	{/each}
</div>
<div role="tabpanel" id={panelId} aria-labelledby={tabId(value)}>
	{@render children()}
</div>

<style>
	.tabs {
		display: grid;
		grid-auto-flow: column;
		grid-auto-columns: 1fr;
		border-bottom: var(--border-width) solid var(--color-border);
	}

	.tab {
		min-height: var(--tap);
		padding: 0 var(--space-2);
		border: none;
		border-bottom: 2px solid transparent;
		background: none;
		color: var(--color-text-quiet);
		font-family: inherit;
		font-size: var(--size-sm);
		font-weight: var(--weight-medium);
		cursor: pointer;
	}

	.tab[aria-selected='true'] {
		color: var(--color-text);
		font-weight: var(--weight-bold);
		border-bottom-color: var(--color-accent);
	}
</style>
