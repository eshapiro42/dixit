export function inviteUrl(gameId: string, origin: string = window.location.origin): string {
	const url = new URL('/', origin);
	url.searchParams.set('game', gameId);
	return url.toString();
}

/** The game ID from a join link, cleaned up to look like one, or null if the URL has none. */
export function gameIdFromUrl(search: string): string | null {
	const raw = new URLSearchParams(search).get('game') ?? '';
	return (
		raw
			.replace(/[^a-z0-9]/gi, '')
			.toUpperCase()
			.slice(0, 4) || null
	);
}

export type ShareResult = 'shared' | 'copied' | 'cancelled' | 'failed';

/** Opens the native share sheet when there is one, otherwise copies the join link. */
export async function shareInvite(
	gameId: string,
	origin: string = window.location.origin
): Promise<ShareResult> {
	const url = inviteUrl(gameId, origin);
	const data = { title: 'Dixit', text: `Join my Dixit game ${gameId}`, url };
	if (navigator.canShare?.(data)) {
		try {
			await navigator.share(data);
			return 'shared';
		} catch (error) {
			return error instanceof DOMException && error.name === 'AbortError' ? 'cancelled' : 'failed';
		}
	}
	try {
		await navigator.clipboard.writeText(url);
		return 'copied';
	} catch {
		return 'failed';
	}
}
