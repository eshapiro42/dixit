export const ZOOM_MIN = 0.6;
export const ZOOM_MAX = 2;

export type ZoomKind = 'hand' | 'table' | 'results';

const STORAGE_PREFIX = 'dixit:zoom:';

function loadStoredZoom(kind: ZoomKind): number {
	try {
		const stored = Number(localStorage.getItem(STORAGE_PREFIX + kind));
		return stored > 0 ? stored : 1;
	} catch {
		return 1;
	}
}

/** One independent zoom preference per card carousel kind (hand/table/results)
 * rather than a single shared one, so sizing the results carousel doesn't
 * also resize the hand. Persists per kind via local storage and stays shared
 * across whichever components currently show that kind (e.g. HostTurn and
 * OtherTurn both show "hand"), so it holds steady across rounds instead of
 * resetting whenever the showing component remounts.
 */
class ZoomState {
	#kind: ZoomKind;
	#value = $state(1);

	constructor(kind: ZoomKind) {
		this.#kind = kind;
		this.#value = loadStoredZoom(kind);
	}

	get value(): number {
		return this.#value;
	}

	set value(next: number) {
		this.#value = next;
		try {
			localStorage.setItem(STORAGE_PREFIX + this.#kind, String(next));
		} catch {
			// Best-effort only: a private window or blocked storage just won't persist.
		}
	}
}

const zoomStates = new Map<ZoomKind, ZoomState>();

export function getZoomState(kind: ZoomKind): ZoomState {
	let state = zoomStates.get(kind);
	if (!state) {
		state = new ZoomState(kind);
		zoomStates.set(kind, state);
	}
	return state;
}
