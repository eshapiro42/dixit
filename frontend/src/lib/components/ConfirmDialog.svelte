<script lang="ts">
	import Button from './Button.svelte';
	import Dialog from './Dialog.svelte';
	import Text from './Text.svelte';

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
	<Text as="p" variant="body" class="confirm-message">{message}</Text>
	<div class="actions">
		<Button kind="secondary" onclick={oncancel}>Cancel</Button>
		<Button kind="danger" onclick={onconfirm}>{confirmLabel}</Button>
	</div>
</Dialog>

<style>
	:global(.confirm-message) {
		margin: 0 0 var(--space-4);
	}

	.actions {
		display: flex;
		justify-content: flex-end;
		gap: var(--space-3);
	}
</style>
