import { describe, expect, it } from 'vitest';
import { phaseLabel, waitingMessage } from './phase';

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

describe('waitingMessage', () => {
	const base = {
		started: true,
		is_creator: false,
		phase: 'host_choosing' as const,
		host: 'alice',
		player_name: 'bob',
		has_played: false,
		has_voted: false,
		votes_cast: 0,
		votes_needed: 2
	};

	it('waits on the storyteller while they write a prompt, but not for the storyteller', () => {
		expect(waitingMessage(base)).toBe('Waiting for alice to write a prompt.');
		expect(waitingMessage({ ...base, player_name: 'alice' })).toBeNull();
	});

	it('waits during card choosing only once this player has nothing left to do', () => {
		const choosing = { ...base, phase: 'others_choosing' as const };
		expect(waitingMessage(choosing)).toBeNull();
		expect(waitingMessage({ ...choosing, has_played: true })).toBe(
			'Waiting for the other players to choose a card.'
		);
		expect(waitingMessage({ ...choosing, player_name: 'alice' })).toBe(
			'Waiting for the other players to choose a card.'
		);
	});

	it('counts votes for the storyteller and waits on voters who have already voted', () => {
		const voting = { ...base, phase: 'voting' as const, votes_cast: 1 };
		expect(waitingMessage({ ...voting, player_name: 'alice' })).toBe('Waiting for votes (1 of 2).');
		expect(waitingMessage(voting)).toBeNull();
		expect(waitingMessage({ ...voting, has_voted: true })).toBe(
			'Waiting for the other players to vote.'
		);
	});

	it('waits for the creator to start only if you are not the creator', () => {
		const lobby = { ...base, started: false, phase: null };
		expect(waitingMessage(lobby)).toBe('Waiting for the creator to start the game.');
		expect(waitingMessage({ ...lobby, is_creator: true })).toBeNull();
	});
});
