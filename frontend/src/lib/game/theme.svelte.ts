export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'dixit:theme';

function currentTheme(): Theme {
	return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
}

class ThemeState {
	#value = $state<Theme>('light');

	constructor() {
		// app.html has already applied the theme before first paint.
		if (typeof document !== 'undefined') this.#value = currentTheme();
	}

	get value(): Theme {
		return this.#value;
	}

	toggle(): void {
		this.#value = this.#value === 'dark' ? 'light' : 'dark';
		document.documentElement.dataset.theme = this.#value;
		try {
			localStorage.setItem(STORAGE_KEY, this.#value);
		} catch {
			// Best-effort only: a private window or blocked storage just won't persist.
		}
	}
}

export const themeState = new ThemeState();
