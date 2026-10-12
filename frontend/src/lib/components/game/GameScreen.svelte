<script lang="ts">
	import type { SessionView } from '../../api/types';
	import { waitingMessage } from '../../game/phase';
	import { gameState } from '../../game/state.svelte';
	import Divider from '../Divider.svelte';
	import ScoreBoard from '../ScoreBoard.svelte';
	import WaitingBar from '../WaitingBar.svelte';
	import HostTurn from './HostTurn.svelte';
	import OtherTurn from './OtherTurn.svelte';
	import Outcome from './Outcome.svelte';
	import Voting from './Voting.svelte';
	import YourHandPanel from './YourHandPanel.svelte';

	let { view }: { view: SessionView } = $props();

	let isHost = $derived(view.host === view.player_name);
</script>

{#if view.phase === 'host_choosing'}
	{#if isHost}
		<HostTurn {view} />
	{:else}
		<YourHandPanel {view} />
	{/if}
{:else if view.phase === 'others_choosing'}
	{#if isHost}
		<YourHandPanel {view} />
	{:else}
		<OtherTurn {view} />
	{/if}
{:else if view.phase === 'voting'}
	<Voting {view} />
	<Divider spacing="section" />
	<YourHandPanel {view} />
{/if}

{#if view.phase !== 'voting' && gameState.lastOutcome}
	<Outcome outcome={gameState.lastOutcome} />
{/if}

<Divider spacing="section" />
<ScoreBoard players={view.players} hostName={view.host} deltas={gameState.lastOutcome?.scores} />

<WaitingBar message={waitingMessage(view)} />
