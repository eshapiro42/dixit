import { afterEach, describe, expect, it, vi } from 'vitest';
import { gameIdFromUrl, inviteUrl, shareInvite } from './invite';

describe('invite links', () => {
	it('builds a join link on the current origin', () => {
		expect(inviteUrl('ABCD', 'https://dixit.example')).toBe('https://dixit.example/?game=ABCD');
	});

	it('reads and normalizes the game id from a query string', () => {
		expect(gameIdFromUrl('?game=abcd')).toBe('ABCD');
		expect(gameIdFromUrl('?game=%20ab12%20')).toBe('AB12');
	});

	it('strips anything that is not part of a game id', () => {
		expect(gameIdFromUrl('?game=%3Cb%3Eabcdef')).toBe('BABC');
		expect(gameIdFromUrl('?game=ab-cd')).toBe('ABCD');
	});

	it('returns null when there is no game id', () => {
		expect(gameIdFromUrl('')).toBeNull();
		expect(gameIdFromUrl('?game=')).toBeNull();
		expect(gameIdFromUrl('?other=1')).toBeNull();
		expect(gameIdFromUrl('?game=%20%21')).toBeNull();
	});
});

describe('shareInvite', () => {
	const origin = 'https://dixit.example';

	afterEach(() => vi.unstubAllGlobals());

	it('uses the native share sheet when there is one', async () => {
		const share = vi.fn().mockResolvedValue(undefined);
		vi.stubGlobal('navigator', { canShare: () => true, share });

		expect(await shareInvite('ABCD', origin)).toBe('shared');
		expect(share).toHaveBeenCalledWith(
			expect.objectContaining({ url: 'https://dixit.example/?game=ABCD' })
		);
	});

	it('reports a dismissed share sheet as cancelled', async () => {
		const share = vi.fn().mockRejectedValue(new DOMException('dismissed', 'AbortError'));
		vi.stubGlobal('navigator', { canShare: () => true, share });

		expect(await shareInvite('ABCD', origin)).toBe('cancelled');
	});

	it('copies the link when sharing is unavailable', async () => {
		const writeText = vi.fn().mockResolvedValue(undefined);
		vi.stubGlobal('navigator', { clipboard: { writeText } });

		expect(await shareInvite('ABCD', origin)).toBe('copied');
		expect(writeText).toHaveBeenCalledWith('https://dixit.example/?game=ABCD');
	});

	it('reports failure when the clipboard is blocked too', async () => {
		const writeText = vi.fn().mockRejectedValue(new Error('denied'));
		vi.stubGlobal('navigator', { clipboard: { writeText } });

		expect(await shareInvite('ABCD', origin)).toBe('failed');
	});
});
