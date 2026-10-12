<script lang="ts">
	import type { SessionView } from '../../api/types';
	import CardRow from '../CardRow.svelte';
	import GamePanel from './GamePanel.svelte';

	let { view }: { view: SessionView } = $props();
</script>

<GamePanel title="Your Hand" zoomKind="hand">
	<CardRow kind="hand" cardIds={view.hand} />
</GamePanel>
