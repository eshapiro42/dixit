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

<dialog bind:this={dialogEl} class:wide onclose={() => onclose()} onclick={handleDialogClick}>
	<div class="header">
		<Text variant="heading">{title}</Text>
		<IconButton label="Close" onclick={() => onclose()} />
	</div>
	<div class="content">
		{@render children()}
	</div>
</dialog>

<style>
	dialog {
		border: none;
		border-radius: var(--radius);
		padding: var(--space-6);
		box-shadow: var(--shadow-overlay);
		max-width: 480px;
		width: 90vw;
	}

	dialog.wide {
		max-width: 640px;
	}

	dialog::backdrop {
		background: rgb(0 0 0 / 0.4);
	}

	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-4);
		margin-bottom: var(--space-4);
	}

	.content {
		display: flex;
		flex-direction: column;
		max-height: 60vh;
		overflow-y: auto;
	}
</style>
