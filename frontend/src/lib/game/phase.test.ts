import { describe, expect, it } from 'vitest';
import { phaseLabel } from './phase';

describe('phaseLabel', () => {
	it('names the host during host_choosing', () => {
		expect(phaseLabel('host_choosing', 'alice')).toBe('alice is choosing a card and a prompt');
	});

	it('falls back when there is no host yet', () => {
		expect(phaseLabel('host_choosing', null)).toBe(
			'The storyteller is choosing a card and a prompt'
		);
	});

	it('describes others_choosing without the prompt', () => {
		expect(phaseLabel('others_choosing', 'alice')).toBe('Other players are choosing cards');
	});

	it('describes voting without the prompt', () => {
		expect(phaseLabel('voting', 'alice')).toBe('Voting');
	});

	it('describes scoring', () => {
		expect(phaseLabel('scoring', 'alice')).toBe('Scoring the round');
	});

	it('describes the lobby when there is no phase yet', () => {
		expect(phaseLabel(null, null)).toBe('Waiting for the game to start');
	});
});
