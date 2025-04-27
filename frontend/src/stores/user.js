import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const usersStore = defineStore('dls-users', () => {
	let userResource = createResource({
		url: 'dls.dls.api.get_user_info',
		onError(error) {
			if (error && error.exc_type === 'AuthenticationError') {
				router.push('/login')
			}
		},
		auto: true,
	})

	const allUsers = createResource({
		url: 'dls.lms.api.get_all_users',
		cache: ['allUsers'],
	})

	return {
		userResource,
		allUsers,
	}
})
