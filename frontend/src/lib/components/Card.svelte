<script lang="ts">
	import { api } from '../api/client';

	interface Props {
		cardId: string;
		selected?: boolean;
		dimmed?: boolean;
		selectable?: boolean;
		onselect?: () => void;
		label?: string;
		votes?: string[];
		delta?: number;
		accessibleLabel?: string;
	}

	let {
		cardId,
		selected = false,
		dimmed = false,
		selectable = false,
		onselect,
		label,
		votes,
		delta,
		accessibleLabel
	}: Props = $props();
</script>

<div class="frame">
	{#if selectable}
		<button
			type="button"
			class="card"
			class:selected
			class:dimmed
			onclick={onselect}
			aria-pressed={selected}
			aria-label={accessibleLabel ?? label ?? 'Card'}
		>
			<img src={api.cardImageUrl(cardId)} alt="" loading="lazy" />
		</button>
	{:else}
		<div class="card" class:selected class:dimmed>
			<img src={api.cardImageUrl(cardId)} alt="" loading="lazy" />
		</div>
	{/if}
	{#if selected}<span class="check" aria-hidden="true">&check;</span>{/if}
	{#if delta !== undefined}<span class="delta" aria-hidden="true">+{delta}</span>{/if}
</div>
{#if label}<span class="label quiet">{label}</span>{/if}
{#each votes ?? [] as voter (voter)}
	<span class="label quiet">{voter}'s vote</span>
{/each}

<style>
	.frame {
		position: relative;
	}

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
			box-shadow 0.15s ease,
			opacity 0.15s ease;
	}

	button.card {
		cursor: pointer;
	}

	button.card:hover {
		transform: translateY(-4px);
		box-shadow: var(--shadow-card-hover);
	}

	button.card:active {
		transform: scale(0.97);
	}

	.card.selected {
		outline: 3px solid var(--color-accent);
		outline-offset: 2px;
	}

	.card.dimmed {
		opacity: 0.55;
	}

	img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.check,
	.delta {
		position: absolute;
		top: var(--space-2);
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-accent);
		color: var(--color-accent-contrast);
		font-weight: 700;
		pointer-events: none;
	}

	.check {
		right: var(--space-2);
		width: 24px;
		height: 24px;
		border-radius: 50%;
		font-size: var(--size-sm);
	}

	.delta {
		left: var(--space-2);
		height: 22px;
		padding: 0 var(--space-2);
		font-size: var(--size-xs);
	}

	.label {
		display: block;
		margin-top: var(--space-1);
		font-size: var(--size-xs);
		text-align: center;
	}
</style>
