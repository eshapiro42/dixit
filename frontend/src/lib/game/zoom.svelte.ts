/** Shared across every card row so a player's preferred size holds steady
 * across rounds instead of resetting whenever a row remounts.
 */
class ZoomState {
	value = $state(1);
}

export const zoomState = new ZoomState();
