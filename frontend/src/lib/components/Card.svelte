<script lang="ts">
	import { api } from '../api/client';

	interface Props {
		cardId: string;
		selected?: boolean;
		selectable?: boolean;
		onselect?: () => void;
		label?: string;
		votes?: string[];
		accessibleLabel?: string;
	}

	let {
		cardId,
		selected = false,
		selectable = false,
		onselect,
		label,
		votes,
		accessibleLabel
	}: Props = $props();
</script>

{#if selectable}
	<button
		type="button"
		class="card"
		class:selected
		onclick={onselect}
		aria-pressed={selected}
		aria-label={accessibleLabel ?? label ?? 'Card'}
	>
		<img src={api.cardImageUrl(cardId)} alt="" loading="lazy" />
	</button>
{:else}
	<div class="card" class:selected>
		<img src={api.cardImageUrl(cardId)} alt="" loading="lazy" />
	</div>
{/if}
{#if label}<span class="label quiet">{label}</span>{/if}
{#each votes ?? [] as voter (voter)}
	<span class="label quiet">{voter}'s vote</span>
{/each}

<style>
	.card {
		display: block;
		width: 100%;
		aspect-ratio: 363 / 527;
		padding: 0;
		border: none;
		border-radius: var(--radius-card);
		overflow: hidden;
		background: var(--color-surface);
		box-shadow: var(--shadow-card);
		cursor: default;
		transition:
			transform 0.15s ease,
			box-shadow 0.15s ease;
	}

	button.card {
		cursor: pointer;
	}

	button.card:hover {
		transform: translateY(-4px);
		box-shadow: var(--shadow-card-hover);
	}

	.card.selected {
		outline: 3px solid var(--color-accent);
		outline-offset: 2px;
	}

	img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.label {
		display: block;
		margin-top: var(--space-1);
		font-size: var(--size-xs);
		text-align: center;
	}
</style>
