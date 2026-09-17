import type { SessionView } from './types';

export class ApiError extends Error {
	status: number;

	constructor(message: string, status: number) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
	}
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const response = await fetch(path, {
		...init,
		credentials: 'same-origin',
		headers: { 'Content-Type': 'application/json', ...init?.headers }
	});
	if (!response.ok) {
		const body = await response.json().catch(() => ({}));
		throw new ApiError(body.error ?? response.statusText, response.status);
	}
	return response.json();
}

function post<T>(path: string, body?: unknown): Promise<T> {
	return request<T>(path, {
		method: 'POST',
		body: body === undefined ? undefined : JSON.stringify(body)
	});
}

export const api = {
	createGame: (playerName: string) => post<SessionView>('/api/games', { player_name: playerName }),
	joinGame: (gameId: string, playerName: string) =>
		post<SessionView>(`/api/games/${gameId}/join`, { player_name: playerName }),
	session: () => request<SessionView>('/api/session'),
	addCpu: () => post<{ ok: true }>('/api/session/add-cpu'),
	start: () => post<{ ok: true }>('/api/session/start'),
	hostChoice: (cardId: string, prompt: string) =>
		post<{ ok: true }>('/api/session/host-choice', { card_id: cardId, prompt }),
	play: (cardId: string) => post<{ ok: true }>('/api/session/play', { card_id: cardId }),
	vote: (cardId: string) => post<{ ok: true }>('/api/session/vote', { card_id: cardId }),
	mulligan: (cardId: string) => post<{ ok: true }>('/api/session/mulligan', { card_id: cardId }),
	cardImageUrl: (cardId: string) => `/api/cards/${cardId}`
};
