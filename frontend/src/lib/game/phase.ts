import type { Phase } from '../api/types';

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
