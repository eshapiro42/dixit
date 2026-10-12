<script lang="ts">
	import type { SessionView } from '../../api/types';
	import CardRow from '../CardRow.svelte';
	import PanelHeader from '../PanelHeader.svelte';
	import Text from '../Text.svelte';
	import ZoomControl from '../ZoomControl.svelte';

	let { view }: { view: SessionView } = $props();
</script>

<section>
	<PanelHeader>
		<Text variant="heading">Your Hand</Text>
		<ZoomControl kind="hand" />
	</PanelHeader>
	<CardRow kind="hand" cardIds={view.hand} />
</section>
