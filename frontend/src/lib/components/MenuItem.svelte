<script lang="ts">
	import type { Snippet } from 'svelte';
	import Icon, { type IconName } from './Icon.svelte';
	import { useMenuId } from './Menu.svelte';

	interface Props {
		onclick: () => void;
		icon: IconName;
		tone?: 'default' | 'danger';
		class?: string;
		children: Snippet;
	}

	let { onclick, icon, tone = 'default', class: className = '', children }: Props = $props();
	const menuId = useMenuId();

	// Hand focus back to the trigger first, so a dialog this opens returns focus there when it closes.
	function activate(): void {
		document.querySelector<HTMLElement>(`[popovertarget="${menuId}"]`)?.focus();
		onclick();
	}
</script>

<button
	type="button"
	class="menu-item {tone} {className}"
	popovertarget={menuId}
	popovertargetaction="hide"
	onclick={activate}
>
	<Icon name={icon} size={18} />
	{@render children()}
</button>

<style>
	.menu-item {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		width: 100%;
		min-height: var(--tap);
		padding: 0 var(--space-3);
		border: none;
		border-radius: var(--radius);
		background: none;
		color: var(--color-text);
		font-family: inherit;
		font-size: var(--size-md);
		font-weight: var(--weight-medium);
		text-align: start;
		cursor: pointer;
	}

	/* Destructive actions sit apart from the rest. */
	.menu-item.danger {
		margin-top: var(--space-1);
		border-top: var(--border-width) solid var(--color-border);
		color: var(--color-danger);
	}

	.menu-item:active {
		background: var(--color-accent-soft);
	}

	@media (hover: hover) {
		.menu-item:hover {
			background: var(--color-accent-soft);
		}
	}
</style>
