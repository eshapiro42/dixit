import { TransientStatus } from './transient.svelte';

/** Copies text and exposes a short-lived "copied"/"failed" status for button feedback. */
export class ClipboardFeedback {
	#status = new TransientStatus<'copied' | 'failed'>();

	get copied(): boolean {
		return this.#status.value === 'copied';
	}

	get failed(): boolean {
		return this.#status.value === 'failed';
	}

	async copy(text: string): Promise<void> {
		try {
			await navigator.clipboard.writeText(text);
			this.#status.show('copied');
		} catch {
			this.#status.show('failed');
		}
	}
}
