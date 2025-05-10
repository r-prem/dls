import { createResource } from 'frappe-ui'



export default function translationPlugin(app) {

	app.config.globalProperties.__ = translate
	window.__ = translate
	// Initialize translations
	if (!window.translatedMessages) {
		fetchTranslations()
	}

	// Listen for language changes
	window.addEventListener('language-change', () => {
		fetchTranslations()
	})
}

function translate(message) {
	let translatedMessages = window.translatedMessages || {}
	let translatedMessage = translatedMessages[message] || message

	const hasPlaceholders = /{\d+}/.test(message)
	if (!hasPlaceholders) {
		return translatedMessage
	}
	return {
		format: function (...args) {
			return translatedMessage.replace(
				/{(\d+)}/g,
				function (match, number) {
					return typeof args[number] != 'undefined'
						? args[number]
						: match
				}
			)
		},
	}
}

function fetchTranslations(lang) {
	createResource({
		url: 'dls.dls.api.get_translations',
		cache: 'translations',
		auto: true,
		transform: (data) => {
			if (data && typeof data === 'object') {
				window.translatedMessages = data
				// Trigger a custom event to notify components about language change
				window.dispatchEvent(new Event('translations-updated'))
			}
		},
		onError: (error) => {
			console.error('Error fetching translations:', error)
			// Set empty translations object to prevent errors
			window.translatedMessages = {}
		},
		onSuccess: () => {
			window.dispatchEvent(new Event('translations-loaded'))
		},
	})
}
