import type { Phase, SessionView } from '../api/types';

/** A few words for the top bar; the fuller sentences live in waitingMessage. */
export function phaseSummary(phase: Phase | null, host: string | null): string {
	switch (phase) {
		case 'host_choosing':
			return `Choosing: ${host ?? 'storyteller'}`;
		case 'others_choosing':
			return 'Choosing cards';
		case 'voting':
			return 'Voting';
		case 'scoring':
			return 'Scoring';
		default:
			return 'Lobby';
	}
}

type WaitingView = Pick<
	SessionView,
	| 'started'
	| 'is_creator'
	| 'phase'
	| 'host'
	| 'player_name'
	| 'has_played'
	| 'has_voted'
	| 'votes_cast'
	| 'votes_needed'
>;

/** What this player is waiting on someone else for, or null. */
export function waitingMessage(view: WaitingView): string | null {
	if (!view.started) {
		return view.is_creator ? null : 'Waiting for the creator to start the game.';
	}
	const isHost = view.host === view.player_name;
	switch (view.phase) {
		case 'host_choosing':
			return isHost ? null : `Waiting for ${view.host ?? 'the storyteller'} to write a prompt.`;
		case 'others_choosing':
			return isHost || view.has_played ? 'Waiting for the other players to choose a card.' : null;
		case 'voting':
			if (isHost) return `Waiting for votes (${view.votes_cast} of ${view.votes_needed}).`;
			return view.has_voted ? 'Waiting for the other players to vote.' : null;
		default:
			return null;
	}
}

/** The storyteller's prompt with who wrote it, or null before there is one. */
export function currentPrompt(
	view: Pick<SessionView, 'host' | 'prompt'>
): { host: string; text: string } | null {
	return view.host && view.prompt ? { host: view.host, text: view.prompt } : null;
}

type LobbyView = Pick<SessionView, 'players' | 'min_players' | 'min_human_players' | 'is_creator'>;

/** What's still missing before the game can start, or null once it can. */
export function startHint(view: LobbyView): string | null {
	const humans = view.players.filter((player) => !player.is_cpu).length;
	const humansNeeded = view.min_human_players - humans;
	const playersNeeded = view.min_players - view.players.length;

	if (humansNeeded > 0) {
		const people = humansNeeded === 1 ? 'person' : 'people';
		return view.is_creator
			? `Invite ${humansNeeded} more ${people} to start.`
			: `Waiting for ${humansNeeded} more ${people} to join.`;
	}
	if (playersNeeded > 0) {
		return view.is_creator
			? `Add ${playersNeeded} more ${playersNeeded === 1 ? 'player or CPU' : 'players or CPUs'} to start.`
			: `Waiting for ${playersNeeded} more ${playersNeeded === 1 ? 'player' : 'players'} to join.`;
	}
	return null;
}
