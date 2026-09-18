<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		title: string;
		open: boolean;
		onclose: () => void;
		children: Snippet;
	}

	let { title, open, onclose, children }: Props = $props();
	let dialogEl: HTMLDialogElement | undefined = $state();

	$effect(() => {
		if (!dialogEl) return;
		if (open && !dialogEl.open) dialogEl.showModal();
		if (!open && dialogEl.open) dialogEl.close();
	});
</script>

<dialog bind:this={dialogEl} onclose={() => onclose()}>
	<div class="header">
		<h2>{title}</h2>
		<button type="button" onclick={() => onclose()} aria-label="Close">&times;</button>
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

	.header h2 {
		font-size: var(--size-lg);
	}

	.header button {
		background: none;
		border: none;
		font-size: var(--size-xl);
		line-height: 1;
		cursor: pointer;
		color: var(--color-text-quiet);
		padding: 0;
	}

	.content {
		max-height: 60vh;
		overflow-y: auto;
	}
</style>
