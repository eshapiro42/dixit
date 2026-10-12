import { ApiError, api } from '../api/client';
import type { GameMessage, RoundOutcome, SessionView } from '../api/types';
import { connectSocket, disconnectSocket } from './socket';

class GameState {
	view = $state<SessionView | null>(null);
	messages = $state<GameMessage[]>([]);
	lastOutcome = $state<RoundOutcome | null>(null);
	outcomes = $state<RoundOutcome[]>([]);
	error = $state<string | null>(null);
	/** Something that happened to the player, shown on the lobby form (not a failure). */
	notice = $state<string | null>(null);

	private connected = false;
	// Bumped by enterSession/leaveGame so a run() call that resolves after the
	// session has already moved on doesn't apply its result to the new session.
	private generation = 0;

	get inGame(): boolean {
		return this.view !== null;
	}

	clearError(): void {
		this.error = null;
	}

	clearNotice(): void {
		this.notice = null;
	}

	async createGame(playerName: string): Promise<void> {
		await this.run(async () => this.enterSession(await api.createGame(playerName), true));
	}

	async joinGame(gameId: string, playerName: string): Promise<void> {
		await this.run(async () => this.enterSession(await api.joinGame(gameId, playerName), true));
	}

	/* Recovers the session quietly. No session yet is normal for a first visit. */
	async tryResume(): Promise<boolean> {
		try {
			this.enterSession(await api.session(), !this.inGame);
			return true;
		} catch {
			return false;
		}
	}

	async addCpu(): Promise<void> {
		await this.run(() => api.addCpu());
	}

	async removePlayer(playerName: string): Promise<void> {
		await this.run(() => api.removePlayer(playerName));
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

	/* Clears the session locally even if the request fails. */
	async leaveGame(): Promise<void> {
		this.generation++;
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
		this.outcomes = [];
		this.error = null;
	}

	private enterSession(view: SessionView, resetHistory: boolean): void {
		this.generation++;
		this.view = view;
		if (resetHistory) {
			this.messages = [...view.messages];
			this.lastOutcome = view.previous_round_outcome;
			this.outcomes = [...view.round_outcomes];
		}
		if (!this.connected) {
			this.subscribe();
			this.connected = true;
		}
	}

	private subscribe(): void {
		const socket = connectSocket();
		socket.on('connect', () => {
			this.tryResume();
		});
		socket.on('state', (data) => {
			if (this.view) Object.assign(this.view, data);
		});
		socket.on('you', (data) => {
			if (this.view) Object.assign(this.view, data);
		});
		socket.on('round_outcome', (data) => {
			this.lastOutcome = data;
			this.outcomes = [...this.outcomes.filter((o) => o.round_number !== data.round_number), data];
		});
		socket.on('message', (data) => {
			this.messages.push(data);
		});
		socket.on('removed', (data) => {
			void this.handleRemoved(data.by);
		});
	}

	private async handleRemoved(by: string): Promise<void> {
		await this.leaveGame();
		this.notice = `${by} removed you from the game.`;
	}

	private async run<T>(action: () => Promise<T>): Promise<T | undefined> {
		const generation = this.generation;
		this.error = null;
		this.notice = null;
		try {
			return await action();
		} catch (err) {
			if (this.generation !== generation) return undefined;
			this.error = err instanceof ApiError ? err.message : 'Something went wrong.';
			return undefined;
		}
	}
}

export const gameState = new GameState();
