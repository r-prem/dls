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
import { generateColorRange, injectPrimaryColorVariables } from '@/utils/colors'
import LoadingScreen from '@/components/Common/LoadingScreen.vue'
const screenSize = useScreenSize()
let { userResource } = usersStore()
const router = useRouter()
const noSidebar = ref(false)
const { branding } = sessionStore()
const translationsLoaded = ref(false)


router.beforeEach((to, from, next) => {
	if (to.query.fromLesson || to.path === '/persona') {
		noSidebar.value = true
	} else {
		noSidebar.value = false
	}
	next()
})

const Layout = computed(() => {
	if (!translationsLoaded.value) {
		console.log('Translations not loaded')
		return LoadingScreen
	}
	console.log('Translations loaded')

	if (noSidebar.value) {
		return NoSidebarLayout
	}
	if (screenSize.width < 640) {
		return MobileLayout
	} else {
		return DesktopLayout
	}
})

onMounted(async () => {
	if (userResource.data) await initTelemetry()
	// Inject primary color variables on app load
	if (branding.data && branding.data.primary_color) {
		injectPrimaryColorVariables(branding.data.primary_color)
	}

	const setLoaded = () => { translationsLoaded.value = true }
  	window.addEventListener('translations-loaded', setLoaded)
  	if (window.translatedMessages) {
   	 translationsLoaded.value = true
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
	window.removeEventListener('translations-loaded', setLoaded)
	stopSession()
})
</script>
