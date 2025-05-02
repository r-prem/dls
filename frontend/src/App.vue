<template>
	<Layout>
		<router-view />
	</Layout>
	<Dialogs />
	<Toasts />
</template>
<script setup>
import { Toasts } from 'frappe-ui'
import { Dialogs } from '@/utils/dialogs'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useScreenSize } from './utils/composables'
import DesktopLayout from './components/DesktopLayout.vue'
import MobileLayout from './components/MobileLayout.vue'
import NoSidebarLayout from './components/NoSidebarLayout.vue'
import { stopSession } from '@/telemetry'
import { init as initTelemetry } from '@/telemetry'
import { usersStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import { generateColorRange } from '@/utils/colors'

const screenSize = useScreenSize()
let { userResource } = usersStore()
const router = useRouter()
const noSidebar = ref(false)
const { branding } = sessionStore()

router.beforeEach((to, from, next) => {
	if (to.query.fromLesson || to.path === '/persona') {
		noSidebar.value = true
	} else {
		noSidebar.value = false
	}
	next()
})

const Layout = computed(() => {
	if (noSidebar.value) {
		return NoSidebarLayout
	}
	if (screenSize.width < 640) {
		return MobileLayout
	} else {
		return DesktopLayout
	}
})

function injectPrimaryColorVariables(primaryColor) {
	if (!primaryColor) return
	const colors = generateColorRange(primaryColor)
	let styleElement = document.getElementById('primary-color-variables')
	if (!styleElement) {
		styleElement = document.createElement('style')
		styleElement.id = 'primary-color-variables'
		document.head.appendChild(styleElement)
	}
	styleElement.textContent = `
		button.bg-surface-gray-7 {
			${Object.entries(colors).map(([key, value]) => `${key}: ${value};`).join('\n')}
		}
		.progress-bar {
			--progress-color: ${colors['--surface-gray-7']};
			--progress-bg: ${colors['--surface-gray-2']};
		}
		.progress-bar-fill {
			background-color: var(--progress-color);
		}
		.progress-bar-bg {
			background-color: var(--progress-bg);
		}
	`
}

onMounted(async () => {
	if (userResource.data) await initTelemetry()
	// Inject primary color variables on app load
	if (branding.data && branding.data.primary_color) {
		injectPrimaryColorVariables(branding.data.primary_color)
	}
})

// Also watch for changes in branding.data.primary_color (in case it loads after mount)
watch(
	() => branding.data && branding.data.primary_color,
	(primaryColor) => {
		if (primaryColor) {
			injectPrimaryColorVariables(primaryColor)
		}
	},
	{ immediate: true }
)

onUnmounted(() => {
	noSidebar.value = false
	stopSession()
})
</script>
