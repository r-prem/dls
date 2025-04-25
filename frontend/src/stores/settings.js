import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource, createDocumentResource } from 'frappe-ui'
import { sessionStore } from './session'

export const useSettings = defineStore('settings', () => {
	const { isLoggedIn } = sessionStore()
	const isSettingsOpen = ref(false)
	const activeTab = ref(null)

	const learningPaths = createResource({
		url: 'lms.lms.api.is_learning_path_enabled',
		auto: true,
		cache: ['learningPath'],
	})

	const allowGuestAccess = createResource({
		url: 'lms.lms.api.is_guest_allowed',
		auto: true,
		cache: ['allowGuestAccess'],
	})

	const paidCoursesEnabled = createResource({
		url: 'lms.lms.api.is_paid_courses_enabled',
		auto: true,
		cache: ['paidCoursesEnabled'],
	})

	const ratingsAllowed = createResource({
		url: 'lms.lms.api.is_ratings_allowed',
		auto: true,
		cache: ['ratingsAllowed'],
	})

	const showEnrolledCount = createResource({
		url: 'lms.lms.api.is_enrolled_count_visible',
		auto: true,
		cache: ['showEnrolledCount'],
	})

	const questionsActive = createResource({
		url: 'lms.lms.api.is_questions_active',
		auto: true,
		cache: ['questionsActive'],
	})

	const displayInstructor = createResource({
		url: 'lms.lms.api.is_instructor_display_enabled',
		auto: true,
		cache: ['displayInstructor'],
	})

	const lessonCompletionTime = createResource({
		url: 'lms.lms.api.get_lesson_completion_time',
		auto: true,
		cache: ['lessonCompletionTime'],
		transform(data) {
			return parseInt(data) || 30
		}
	})

	return {
		isSettingsOpen,
		activeTab,
		learningPaths,
		allowGuestAccess,
		paidCoursesEnabled,
		ratingsAllowed,
		showEnrolledCount,
		questionsActive,
		displayInstructor,
		lessonCompletionTime,
	}
})
