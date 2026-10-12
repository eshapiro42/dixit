/** A status that sets itself back to null after a short while, for button feedback. */
export class TransientStatus<T extends string> {
	value = $state<T | null>(null);
	#timeout: ReturnType<typeof setTimeout> | undefined;

	show(status: T, ms = 1500): void {
		this.value = status;
		clearTimeout(this.#timeout);
		this.#timeout = setTimeout(() => (this.value = null), ms);
	}
}
