import { describe, expect, it } from 'vitest';
import { phaseSummary, waitingMessage } from './phase';

describe('phaseSummary', () => {
	it('names the host while they are choosing', () => {
		expect(phaseSummary('host_choosing', 'alice')).toBe('Choosing: alice');
	});

	it('falls back when there is no host yet', () => {
		expect(phaseSummary('host_choosing', null)).toBe('Choosing: storyteller');
	});

	it('keeps the other phases to a couple of words', () => {
		expect(phaseSummary('others_choosing', 'alice')).toBe('Choosing cards');
		expect(phaseSummary('voting', 'alice')).toBe('Voting');
		expect(phaseSummary('scoring', 'alice')).toBe('Scoring');
	});

	it('calls the pre-game state the lobby', () => {
		expect(phaseSummary(null, null)).toBe('Lobby');
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
