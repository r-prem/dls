import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource, createDocumentResource } from 'frappe-ui'
import { sessionStore } from './session'

export const useSettings = defineStore('settings', () => {
	const { isLoggedIn } = sessionStore()
	const isSettingsOpen = ref(false)
	const activeTab = ref(null)

	const learningPaths = createResource({
		url: 'dls.dls.api.is_learning_path_enabled',
		auto: true,
		cache: ['learningPath'],
	})

	const allowGuestAccess = createResource({
		url: 'dls.dls.api.is_guest_allowed',
		auto: true,
		cache: ['allowGuestAccess'],
	})

	const paidCoursesEnabled = createResource({
		url: 'dls.dls.api.is_paid_courses_enabled',
		auto: true,
		cache: ['paidCoursesEnabled'],
	})

	const ratingsAllowed = createResource({
		url: 'dls.dls.api.is_ratings_allowed',
		auto: true,
		cache: ['ratingsAllowed'],
	})

	const showEnrolledCount = createResource({
		url: 'dls.dls.api.is_enrolled_count_visible',
		auto: true,
		cache: ['showEnrolledCount'],
	})

	const questionsActive = createResource({
		url: 'dls.dls.api.is_questions_active',
		auto: true,
		cache: ['questionsActive'],
	})

	const displayInstructor = createResource({
		url: 'dls.dls.api.is_instructor_display_enabled',
		auto: true,
		cache: ['displayInstructor'],
	})

	const lessonCompletionTime = createResource({
		url: 'dls.dls.api.get_lesson_completion_time',
		auto: true,
		cache: ['lessonCompletionTime'],
		transform(data) {
			return parseInt(data) || 30
		}
	})

	const certificatesEnabled = createResource({
		url: 'dls.dls.api.is_certificates_enabled',
		auto: true,
		cache: ['certificatesEnabled'],
	})

	const quizzesEnabled = createResource({
		url: 'dls.dls.api.is_quizzes_enabled',
		auto: true,
		cache: ['quizzesEnabled'],
	})

	const maxCourses = createResource({
		url: 'dls.dls.api.get_max_courses',
		auto: true,
		cache: ['maxCourses'],
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
		certificatesEnabled,
		quizzesEnabled,
		maxCourses,
	}
})
