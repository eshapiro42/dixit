<script lang="ts">
	import Button from './Button.svelte';
	import Dialog from './Dialog.svelte';

	interface Props {
		open: boolean;
		title: string;
		message: string;
		confirmLabel?: string;
		onconfirm: () => void;
		oncancel: () => void;
	}

	let { open, title, message, confirmLabel = 'Confirm', onconfirm, oncancel }: Props = $props();
</script>

<Dialog {title} {open} onclose={oncancel}>
	<p class="message">{message}</p>
	<div class="actions">
		<Button kind="secondary" onclick={oncancel}>Cancel</Button>
		<Button kind="danger" onclick={onconfirm}>{confirmLabel}</Button>
	</div>
</Dialog>

<style>
	.message {
		margin: 0 0 var(--space-4);
	}

	.actions {
		display: flex;
		justify-content: flex-end;
		gap: var(--space-3);
	}
</style>
