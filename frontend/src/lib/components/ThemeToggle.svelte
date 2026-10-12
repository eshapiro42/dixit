<script lang="ts">
	import { themeState } from '../game/theme.svelte';

	let isDark = $derived(themeState.value === 'dark');
</script>

<button
	type="button"
	class="theme-toggle"
	aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
	onclick={() => themeState.toggle()}
>
	<svg
		viewBox="0 0 24 24"
		width="20"
		height="20"
		aria-hidden="true"
		fill="none"
		stroke="currentColor"
		stroke-width="2"
		stroke-linecap="round"
		stroke-linejoin="round"
	>
		{#if isDark}
			<circle cx="12" cy="12" r="4" />
			<path
				d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
			/>
		{:else}
			<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
		{/if}
	</svg>
</button>

<style>
	.theme-toggle {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: var(--tap);
		height: var(--tap);
		padding: 0;
		border: none;
		border-radius: var(--radius);
		background: none;
		color: var(--color-text-quiet);
		cursor: pointer;
		transition:
			background-color 0.15s ease,
			color 0.15s ease;
	}

	.theme-toggle:hover {
		background: var(--color-accent-soft);
		color: var(--color-text);
	}

	.theme-toggle:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: 1px;
	}
</style>
