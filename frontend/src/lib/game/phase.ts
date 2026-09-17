import type { Phase } from '../api/types';

export function phaseLabel(
	phase: Phase | null,
	host: string | null,
	prompt: string | null
): string {
	switch (phase) {
		case 'host_choosing':
			return `${host ?? 'The storyteller'} is choosing a card and a prompt`;
		case 'others_choosing':
			return prompt ? `Match the prompt: "${prompt}"` : 'Choosing cards';
		case 'voting':
			return prompt ? `Vote for the card that matches: "${prompt}"` : 'Voting';
		case 'scoring':
			return 'Scoring the round';
		default:
			return 'Waiting for the game to start';
	}
}
