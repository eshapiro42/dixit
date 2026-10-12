/** The card a player has picked from a row, dropped again once the card leaves it. */
export class CardSelection {
	selectedId = $state<string | null>(null);

	/** Call during component setup: the selection prunes itself as the row changes. */
	constructor(cards: () => string[], onPruned?: () => void) {
		$effect(() => {
			if (this.selectedId !== null && !cards().includes(this.selectedId)) {
				this.selectedId = null;
				onPruned?.();
			}
		});
	}

	toggle(id: string): void {
		this.selectedId = this.selectedId === id ? null : id;
	}

	clear(): void {
		this.selectedId = null;
	}
}
