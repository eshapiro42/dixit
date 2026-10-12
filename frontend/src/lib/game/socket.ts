import { io, type Socket } from 'socket.io-client';
import type { GameMessage, PrivateView, PublicView, RoundOutcome } from '../api/types';

interface ServerToClientEvents {
	state: (data: PublicView) => void;
	you: (data: PrivateView) => void;
	message: (data: GameMessage) => void;
	round_outcome: (data: RoundOutcome) => void;
}

let socket: Socket<ServerToClientEvents> | undefined;

export function connectSocket(): Socket<ServerToClientEvents> {
	if (!socket) {
		socket = io({ path: '/socket.io', transports: ['websocket'] });
	}
	return socket;
}

export function disconnectSocket(): void {
	socket?.disconnect();
	socket = undefined;
}
