import type { Phase, SessionView } from '../api/types';

export function phaseLabel(phase: Phase | null, host: string | null): string {
	switch (phase) {
		case 'host_choosing':
			return `${host ?? 'The storyteller'} is choosing a card and a prompt`;
		case 'others_choosing':
			return 'Other players are choosing cards';
		case 'voting':
			return 'Voting';
		case 'scoring':
			return 'Scoring the round';
		default:
			return 'Waiting for the game to start';
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

/** What this player is currently waiting on someone else to do, or null when
 * the ball is in their own court (or there's nothing to wait for). */
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
