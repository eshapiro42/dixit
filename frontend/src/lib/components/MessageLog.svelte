<script lang="ts">
	import type { GameMessage } from '../api/types';

	interface Props {
		messages: GameMessage[];
	}

	let { messages }: Props = $props();
	let listEl: HTMLElement | undefined;

	$effect(() => {
		const count = messages.length;
		if (count > 0) listEl?.scrollTo({ top: listEl.scrollHeight });
	});
</script>

<div class="log" bind:this={listEl}>
	{#each messages as message, index (index)}
		<p class:emphasis={message.emphasis}>{message.text}</p>
	{/each}
</div>

<style>
	.log {
		display: flex;
		flex-direction: column;
		gap: var(--space-1);
		overflow-y: auto;
		max-height: 100%;
		font-size: var(--size-sm);
	}

	p {
		margin: 0;
		color: var(--color-text-quiet);
	}

	p.emphasis {
		color: var(--color-text);
		font-weight: 600;
	}
</style>
