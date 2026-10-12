<script lang="ts">
	import { ClipboardFeedback } from '../game/clipboard.svelte';
	import { shareInvite } from '../game/invite';
	import { TransientStatus } from '../game/transient.svelte';
	import Button from './Button.svelte';
	import Icon from './Icon.svelte';
	import Stat from './Stat.svelte';
	import Text from './Text.svelte';

	let { gameId }: { gameId: string } = $props();

	const clipboard = new ClipboardFeedback();
	const shared = new TransientStatus<'copied' | 'failed'>();

	async function share(): Promise<void> {
		const result = await shareInvite(gameId);
		if (result === 'copied' || result === 'failed') shared.show(result);
	}

	let shareLabel = $derived(
		shared.value === 'copied'
			? 'Link copied'
			: shared.value === 'failed'
				? "Couldn't share"
				: 'Share'
	);
	let copyLabel = $derived(
		clipboard.copied ? 'Copied' : clipboard.failed ? "Couldn't copy" : 'Copy'
	);
</script>

<div class="invite">
	<div class="code">
		<Text as="span" variant="label">Game ID</Text>
		<Stat size="hero">{gameId}</Stat>
	</div>
	<div class="buttons">
		<Button kind="secondary" onclick={() => clipboard.copy(gameId)}>
			<Icon name={clipboard.copied ? 'check' : 'copy'} size={16} />
			{copyLabel}
		</Button>
		<Button kind="secondary" onclick={share}>
			<Icon name={shared.value === 'copied' ? 'check' : 'share'} size={16} />
			{shareLabel}
		</Button>
	</div>
	<span class="sr-only" role="status">
		{clipboard.copied
			? 'Game ID copied'
			: shared.value === 'copied'
				? 'Join link copied'
				: clipboard.failed || shared.value === 'failed'
					? 'Copy failed'
					: ''}
	</span>
</div>

<style>
	.invite {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
		padding: var(--space-4);
		border: var(--border-width) solid var(--color-border);
	}

	.code {
		display: flex;
		flex-direction: column;
		gap: var(--space-1);
	}

	.buttons {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-3);
	}
</style>
