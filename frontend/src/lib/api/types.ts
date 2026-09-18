export type Phase = 'host_choosing' | 'others_choosing' | 'voting' | 'scoring';

export interface PlayerSummary {
	name: string;
	score: number;
	is_cpu: boolean;
}

export interface RoundOutcome {
	host: string;
	round_number: number;
	prompt: string | null;
	table: Record<string, string>;
	votes: Record<string, string>;
	scores: Record<string, number>;
	correct_voter_count: number;
}

export interface PublicView {
	game_id: string;
	creator_name: string;
	started: boolean;
	playable: boolean;
	min_players: number;
	min_human_players: number;
	players: PlayerSummary[];
	phase: Phase | null;
	host: string | null;
	prompt: string | null;
	table: string[] | null;
	votes_cast: number;
	votes_needed: number;
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
	round_start: boolean;
}
