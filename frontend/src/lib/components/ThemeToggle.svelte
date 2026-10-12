<script lang="ts">
	import { themeState } from '../game/theme.svelte';
	import IconButton from './IconButton.svelte';
</script>

<IconButton
	icon={themeState.other === 'light' ? 'sun' : 'moon'}
	label="Switch to {themeState.other} theme"
	onclick={() => themeState.toggle()}
/>
