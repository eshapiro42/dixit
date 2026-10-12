import { describe, expect, it } from 'vitest';
import { phaseSummary, startHint, waitingMessage } from './phase';

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

describe('startHint', () => {
	const human = (name: string) => ({ name, score: 0, is_cpu: false });
	const cpu = (name: string) => ({ name, score: 0, is_cpu: true });
	const lobby = (players: ReturnType<typeof human>[], isCreator = true) => ({
		players,
		min_players: 4,
		min_human_players: 3,
		is_creator: isCreator
	});

	it('asks the creator to invite people while humans are short', () => {
		expect(startHint(lobby([human('a')]))).toBe('Invite 2 more people to start.');
		expect(startHint(lobby([human('a'), human('b')]))).toBe('Invite 1 more person to start.');
	});

	it('asks the creator to fill the remaining seats once there are enough humans', () => {
		const three = [human('a'), human('b'), human('c')];
		expect(startHint(lobby(three))).toBe('Add 1 more player or CPU to start.');
	});

	it('counts CPUs as players but not as people', () => {
		const players = [human('a'), human('b'), cpu('CPU 1'), cpu('CPU 2')];
		expect(startHint(lobby(players))).toBe('Invite 1 more person to start.');
	});

	it('is null once the game can start', () => {
		const ready = [human('a'), human('b'), human('c'), cpu('CPU 1')];
		expect(startHint(lobby(ready))).toBeNull();
	});

	it('words it as waiting for everyone who is not the creator', () => {
		expect(startHint(lobby([human('a')], false))).toBe('Waiting for 2 more people to join.');
	});
});
