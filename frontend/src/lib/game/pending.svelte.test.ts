import { describe, expect, it } from 'vitest';
import { PendingAction } from './pending.svelte';

describe('PendingAction', () => {
	it('is pending only while the action runs', async () => {
		const action = new PendingAction();
		let release!: () => void;
		const running = action.run(() => new Promise<void>((resolve) => (release = resolve)));

		expect(action.pending).toBe(true);
		release();
		await running;
		expect(action.pending).toBe(false);
	});

	it('clears the flag even when the action throws', async () => {
		const action = new PendingAction();

		await expect(
			action.run(async () => {
				throw new Error('boom');
			})
		).rejects.toThrow('boom');
		expect(action.pending).toBe(false);
	});
});
