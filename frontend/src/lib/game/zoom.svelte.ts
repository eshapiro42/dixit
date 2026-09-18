const STORAGE_KEY = 'dixit:zoom';

function loadStoredZoom(): number {
	try {
		const stored = Number(localStorage.getItem(STORAGE_KEY));
		return stored > 0 ? stored : 1;
	} catch {
		return 1;
	}
}

/** Shared across every card row so a player's preferred size holds steady
 * across rounds instead of resetting whenever a row remounts, and persists
 * across visits via local storage.
 */
class ZoomState {
	#value = $state(loadStoredZoom());

	get value(): number {
		return this.#value;
	}

	set value(next: number) {
		this.#value = next;
		try {
			localStorage.setItem(STORAGE_KEY, String(next));
		} catch {
			// Best-effort only: a private window or blocked storage just won't persist.
		}
	}
}

export const zoomState = new ZoomState();
