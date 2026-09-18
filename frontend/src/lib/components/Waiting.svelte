<script lang="ts">
	interface Props {
		detail: string;
	}

	let { detail }: Props = $props();
</script>

<section>
	<h2>Waiting</h2>
	<p class="quiet">{detail}</p>
</section>
