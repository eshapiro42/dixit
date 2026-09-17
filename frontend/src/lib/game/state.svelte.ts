import { ApiError, api } from '../api/client';
import type { GameMessage, RoundOutcome, SessionView } from '../api/types';
import { connectSocket, disconnectSocket } from './socket';

const MAX_MESSAGES = 100;

class GameState {
	view = $state<SessionView | null>(null);
	messages = $state<GameMessage[]>([]);
	lastOutcome = $state<RoundOutcome | null>(null);
	error = $state<string | null>(null);

	private connected = false;

	get inGame(): boolean {
		return this.view !== null;
	}

	clearError(): void {
		this.error = null;
	}

	async createGame(playerName: string): Promise<void> {
		await this.run(async () => this.enterSession(await api.createGame(playerName)));
	}

	async joinGame(gameId: string, playerName: string): Promise<void> {
		await this.run(async () => this.enterSession(await api.joinGame(gameId, playerName)));
	}

	/** Silently recover an existing session (e.g. after a page reload). No session yet is
	 * the expected outcome for a first-time visitor, not an error worth showing.
	 */
	async tryResume(): Promise<boolean> {
		try {
			this.enterSession(await api.session());
			return true;
		} catch {
			return false;
		}
	}

	async addCpu(): Promise<void> {
		await this.run(() => api.addCpu());
	}

	async start(): Promise<void> {
		await this.run(() => api.start());
	}

	async hostChoice(cardId: string, prompt: string): Promise<void> {
		await this.run(() => api.hostChoice(cardId, prompt));
	}

	async play(cardId: string): Promise<void> {
		await this.run(() => api.play(cardId));
	}

	async vote(cardId: string): Promise<void> {
		await this.run(() => api.vote(cardId));
	}

	async mulligan(cardId: string): Promise<void> {
		await this.run(() => api.mulligan(cardId));
	}

	/** Leave the current game and return to the lobby form. The session is cleared
	 * locally even if the request fails: there's nothing useful to retry here.
	 */
	async leaveGame(): Promise<void> {
		try {
			await api.leave();
		} catch {
			// already leaving regardless
		}
		disconnectSocket();
		this.connected = false;
		this.view = null;
		this.messages = [];
		this.lastOutcome = null;
		this.error = null;
	}

	private enterSession(view: SessionView): void {
		this.view = view;
		this.messages = [];
		this.lastOutcome = view.previous_round_outcome;
		if (!this.connected) {
			this.subscribe();
			this.connected = true;
		}
	}

	private subscribe(): void {
		const socket = connectSocket();
		socket.on('state', (data) => {
			if (this.view) Object.assign(this.view, data);
		});
		socket.on('you', (data) => {
			if (this.view) Object.assign(this.view, data);
		});
		socket.on('round_outcome', (data) => {
			this.lastOutcome = data;
		});
		socket.on('message', (data) => {
			this.messages.push(data);
			if (this.messages.length > MAX_MESSAGES) this.messages.shift();
		});
	}

	private async run<T>(action: () => Promise<T>): Promise<T | undefined> {
		this.error = null;
		try {
			return await action();
		} catch (err) {
			this.error = err instanceof ApiError ? err.message : 'Something went wrong.';
			return undefined;
		}
	}
}

export const gameState = new GameState();
