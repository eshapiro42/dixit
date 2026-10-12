<script lang="ts">
	import type { Snippet } from 'svelte';
	import IconButton from './IconButton.svelte';
	import Text from './Text.svelte';

	interface Props {
		title: string;
		open: boolean;
		wide?: boolean;
		onclose: () => void;
		children: Snippet;
	}

	let { title, open, wide = false, onclose, children }: Props = $props();
	let dialogEl: HTMLDialogElement | undefined = $state();
	const titleId = $props.id();

	$effect(() => {
		if (!dialogEl) return;
		if (open && !dialogEl.open) dialogEl.showModal();
		if (!open && dialogEl.open) dialogEl.close();
	});

	// A click in the dialog's padding also targets the dialog, so check the coordinates.
	function handleDialogClick(event: MouseEvent): void {
		if (!dialogEl || event.target !== dialogEl) return;
		const rect = dialogEl.getBoundingClientRect();
		const clickedInside =
			event.clientX >= rect.left &&
			event.clientX <= rect.right &&
			event.clientY >= rect.top &&
			event.clientY <= rect.bottom;
		if (!clickedInside) onclose();
	}
</script>

<dialog
	bind:this={dialogEl}
	aria-labelledby={titleId}
	class:wide
	onclose={() => onclose()}
	onclick={handleDialogClick}
>
	<div class="header">
		<Text variant="heading" id={titleId}>{title}</Text>
		<IconButton icon="close" label="Close" onclick={() => onclose()} />
	</div>
	<div class="content">
		{@render children()}
	</div>
</dialog>

<style>
	dialog {
		width: min(30rem, calc(100% - 2 * var(--space-4)));
		max-height: calc(100dvh - 2 * var(--space-4));
		padding: var(--space-4) var(--space-4) var(--space-6);
		border: var(--border-width) solid var(--color-border);
		border-radius: var(--radius);
		background: var(--color-surface-raised);
		color: var(--color-text);
		box-shadow: var(--shadow-overlay);
		overscroll-behavior: contain;
	}

	dialog[open] {
		display: flex;
		flex-direction: column;
	}

	dialog.wide {
		width: min(40rem, calc(100% - 2 * var(--space-4)));
	}

	dialog::backdrop {
		background: var(--color-backdrop);
	}

	@media (min-width: 40rem) {
		dialog {
			padding: var(--space-6);
		}
	}

	.header {
		display: flex;
		flex-shrink: 0;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-4);
		margin-bottom: var(--space-2);
	}

	.content {
		display: flex;
		flex-direction: column;
		flex: 1 1 auto;
		min-height: 0;
		overflow-y: auto;
		overscroll-behavior: contain;
	}
</style>
