<script module lang="ts">
	export type IconName =
		'close' | 'menu' | 'sun' | 'moon' | 'copy' | 'check' | 'share' | 'fit' | 'log' | 'leave';
</script>

<script lang="ts">
	const PATHS: Record<IconName, string> = {
		close: 'M6 6l12 12M18 6L6 18',
		menu: 'M5 7h14M5 12h14M5 17h14',
		sun: 'M12 8a4 4 0 100 8 4 4 0 000-8zM12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41',
		moon: 'M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z',
		copy: 'M9 9h10v10H9zM5 15V5h10',
		check: 'M5 12.5l4.5 4.5L19 7.5',
		share: 'M12 15V4M8 8l4-4 4 4M5 13v6h14v-6',
		fit: 'M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5',
		log: 'M5 6h14M5 11h14M5 16h9',
		leave: 'M10 5H5v14h5M14 8l4 4-4 4M18 12H9'
	};

	interface Props {
		name: IconName;
		size?: number;
	}

	let { name, size = 20 }: Props = $props();
</script>

<svg
	viewBox="0 0 24 24"
	width={size}
	height={size}
	fill="none"
	stroke="currentColor"
	stroke-width="2"
	stroke-linecap="round"
	stroke-linejoin="round"
	aria-hidden="true"
>
	<path d={PATHS[name]} />
</svg>
