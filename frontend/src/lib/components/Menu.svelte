<script module lang="ts">
	import { getContext } from 'svelte';

	const MENU_KEY = Symbol('menu');

	/** The id of the enclosing Menu's popover, so an item can close it. */
	export function useMenuId(): string {
		return getContext<string>(MENU_KEY);
	}
</script>

<script lang="ts">
	import { setContext, type Snippet } from 'svelte';
	import IconButton from './IconButton.svelte';

	interface Props {
		label?: string;
		children: Snippet;
	}

	let { label = 'Menu', children }: Props = $props();

	const id = $props.id();
	setContext(MENU_KEY, id);
	let open = $state(false);
</script>

<IconButton icon="menu" {label} popovertarget={id} aria-expanded={open} />
<div
	{id}
	class="menu"
	role="group"
	aria-label={label}
	popover="auto"
	ontoggle={(event) => (open = event.newState === 'open')}
>
	{@render children()}
</div>

<style>
	/* Under the bar on wide screens, a bottom sheet on phones. */
	.menu {
		position: fixed;
		inset: var(--topbar-h) auto auto auto;
		inset-inline-end: max(
			var(--page-gutter),
			calc((100% - var(--page-max)) / 2 + var(--page-gutter))
		);
		margin: 0;
		min-width: 14rem;
		padding: var(--space-1);
		border: var(--border-width) solid var(--color-border);
		background: var(--color-surface-raised);
		color: var(--color-text);
		box-shadow: var(--shadow-overlay);
	}

	.menu::backdrop {
		background: var(--color-backdrop);
	}

	@media (max-width: 39.999rem) {
		.menu {
			inset: auto 0 0 0;
			width: 100%;
			padding: var(--space-2) var(--page-gutter) max(var(--space-4), env(safe-area-inset-bottom));
			border-inline: none;
			border-bottom: none;
		}
	}

	@media (hover: hover) {
		.menu::backdrop {
			background: transparent;
		}
	}

	.menu:popover-open {
		animation: menu-in 0.16s ease-out;
	}

	@keyframes menu-in {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
	}
</style>
