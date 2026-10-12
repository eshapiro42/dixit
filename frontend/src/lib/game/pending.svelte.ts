/** Tracks whether an async action is in flight, so its button can disable itself. */
export class PendingAction {
	pending = $state(false);

	async run(action: () => Promise<unknown>): Promise<void> {
		this.pending = true;
		try {
			await action();
		} finally {
			this.pending = false;
		}
	}
}
