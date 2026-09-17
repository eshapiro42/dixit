export type Phase = 'host_choosing' | 'others_choosing' | 'voting' | 'scoring';

export interface PlayerSummary {
	name: string;
	score: number;
	is_cpu: boolean;
}

export interface RoundOutcome {
	host: string;
	prompt: string | null;
	table: Record<string, string>;
	votes: Record<string, string>;
}

export interface PublicView {
	game_id: string;
	started: boolean;
	playable: boolean;
	players: PlayerSummary[];
	phase: Phase | null;
	host: string | null;
	prompt: string | null;
	table: string[] | null;
}

export interface PrivateView {
	player_name: string;
	is_creator: boolean;
	hand: string[];
	mulligan_available: boolean;
	has_played: boolean;
	has_voted: boolean;
}

export interface SessionView extends PublicView, PrivateView {
	previous_round_outcome: RoundOutcome | null;
}

export interface GameMessage {
	text: string;
	emphasis: boolean;
}
