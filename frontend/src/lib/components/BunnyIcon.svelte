<script lang="ts">
	import { BUNNY_PATH, BUNNY_TRANSFORM, BUNNY_VIEWBOX } from '../bunny';

	interface Props {
		class?: string;
	}

	let { class: className = '' }: Props = $props();
</script>

<svg class={className} viewBox={BUNNY_VIEWBOX} aria-hidden="true">
	<g transform={BUNNY_TRANSFORM}>
		<path d={BUNNY_PATH} />
	</g>
</svg>
