<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { ZoomKind } from '../../game/zoom.svelte';
	import PanelHeader from '../PanelHeader.svelte';
	import PromptCaption from '../PromptCaption.svelte';
	import Text from '../Text.svelte';
	import ZoomControl from '../ZoomControl.svelte';

	interface Props {
		title: string;
		zoomKind: ZoomKind;
		/** Marks the panel the player can act on right now. */
		actionNeeded?: boolean;
		prompt?: { host: string; text: string } | null;
		children: Snippet;
		actions?: Snippet;
	}

	let { title, zoomKind, actionNeeded = false, prompt = null, children, actions }: Props = $props();
</script>

<section class="panel" class:action-needed={actionNeeded}>
	<PanelHeader>
		<Text variant="heading">{title}</Text>
		<ZoomControl kind={zoomKind} />
	</PanelHeader>
	{#if prompt}
		<PromptCaption host={prompt.host} prompt={prompt.text} />
	{/if}
	{@render children()}
	{#if actions}{@render actions()}{/if}
</section>

<style>
	.panel {
		position: relative;
	}

	/* An accent bar at the page edge, and a one-time flash when the panel first appears. */
	.action-needed {
		animation: action-flash 1s ease-out;
	}

	.action-needed::before {
		content: '';
		position: absolute;
		top: 0.15em;
		bottom: 0.15em;
		left: calc(-1 * var(--page-gutter));
		width: var(--accent-line);
		background: var(--color-accent);
	}

	@keyframes action-flash {
		from {
			background: var(--color-accent-soft);
		}
		to {
			background: transparent;
		}
	}
</style>
