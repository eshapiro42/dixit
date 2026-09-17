import { describe, expect, it } from 'vitest';
import { phaseLabel } from './phase';

describe('phaseLabel', () => {
	it('names the host during host_choosing', () => {
		expect(phaseLabel('host_choosing', 'alice', null)).toBe(
			'alice is choosing a card and a prompt'
		);
	});

	it('falls back when there is no host yet', () => {
		expect(phaseLabel('host_choosing', null, null)).toBe(
			'The storyteller is choosing a card and a prompt'
		);
	});

	it('quotes the prompt during others_choosing', () => {
		expect(phaseLabel('others_choosing', 'alice', 'a rainy afternoon')).toBe(
			'Match the prompt: "a rainy afternoon"'
		);
	});

	it('quotes the prompt while voting', () => {
		expect(phaseLabel('voting', 'alice', 'a rainy afternoon')).toBe(
			'Vote for the card that matches: "a rainy afternoon"'
		);
	});

	it('describes scoring with no prompt needed', () => {
		expect(phaseLabel('scoring', 'alice', 'a rainy afternoon')).toBe('Scoring the round');
	});

	it('describes the lobby when there is no phase yet', () => {
		expect(phaseLabel(null, null, null)).toBe('Waiting for the game to start');
	});
});
