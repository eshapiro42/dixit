<script lang="ts">
	interface Props {
		spacing?: 'section' | 'none';
	}

	let { spacing = 'section' }: Props = $props();
</script>

<hr class="divider divider--{spacing}" />

<style>
	.divider {
		border: none;
		border-top: var(--border-width) solid var(--color-border);
		margin: 0;
	}

	.divider--section {
		margin: var(--space-8) 0;
	}
</style>
