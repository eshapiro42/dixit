import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, api } from './client';

describe('api client', () => {
	beforeEach(() => {
		vi.stubGlobal('fetch', vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it('resolves with the parsed body on success', async () => {
		vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }));
		await expect(api.start()).resolves.toEqual({ ok: true });
	});

	it('sends json bodies with the player name', async () => {
		vi.mocked(fetch).mockResolvedValue(new Response('{}', { status: 200 }));
		await api.createGame('alice');
		const [path, init] = vi.mocked(fetch).mock.calls[0];
		expect(path).toBe('/api/games');
		expect(init?.method).toBe('POST');
		expect(JSON.parse(init?.body as string)).toEqual({ player_name: 'alice' });
	});

	it('throws an ApiError carrying the server message and status', async () => {
		vi.mocked(fetch).mockResolvedValue(
			new Response(JSON.stringify({ error: 'Game X was not found.' }), { status: 404 })
		);
		await expect(api.session()).rejects.toMatchObject(new ApiError('Game X was not found.', 404));
	});

	it('falls back to the status text when the body is not json', async () => {
		vi.mocked(fetch).mockResolvedValue(
			new Response('not json', { status: 500, statusText: 'Server Error' })
		);
		await expect(api.session()).rejects.toMatchObject(new ApiError('Server Error', 500));
	});
});
