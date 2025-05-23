<template>
	<div class="">
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
		>
			<Breadcrumbs
				class="h-7"
				:items="[{ label: __('Jobs'), route: { name: 'Jobs' } }]"
			/>
			<router-link
				v-if="user.data?.name"
				:to="{
					name: 'JobCreation',
					params: {
						jobName: 'new',
					},
				}"
			>
				<Button variant="solid">
					<template #prefix>
						<Plus class="h-4 w-4" />
					</template>
					{{ __('New Job') }}
				</Button>
			</router-link>
		</header>
		<div>
			<div v-if="jobs.data?.length" class="p-5">
				<div
					class="flex flex-col lg:flex-row space-y-4 lg:space-y-0 lg:items-center justify-between mb-5"
				>
					<div class="text-xl text-ink-gray-9 font-semibold">
						{{ __('Find the perfect job for you') }}
					</div>
					<div class="grid grid-cols-2 gap-2">
						<FormControl
							type="text"
							:placeholder="__('Search')"
							v-model="searchQuery"
							class="min-w-40 lg:min-w-0 lg:w-32 xl:w-40"
							@input="updateJobs"
						>
							<template #prefix>
								<Search
									class="w-4 h-4 stroke-1.5 text-ink-gray-5"
									name="search"
								/>
							</template>
						</FormControl>
						<FormControl
							v-model="jobType"
							type="select"
							:options="jobTypes"
							class="min-w-40 lg:min-w-0 lg:w-32 xl:w-40"
							:placeholder="__('Type')"
							@change="updateJobs"
						/>
					</div>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
					<router-link
						v-for="job in jobs.data"
						:to="{
							name: 'JobDetail',
							params: { job: job.name },
						}"
						:key="job.name"
					>
						<JobCard :job="job" />
					</router-link>
				</div>
			</div>
			<div
				v-else
				class="flex flex-col items-center justify-center text-sm text-ink-gray-5 mt-48"
			>
				<Laptop class="size-10 mx-auto stroke-1 text-ink-gray-4" />
				<div class="text-lg font-medium mb-1">
					{{ __('No jobs found') }}
				</div>
				<div class="leading-5 w-2/5 text-center">
					{{
						__(
							'There are no jobs available at the moment. Open a job opportunity or check here again later.'
						)
					}}
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import {
	Button,
	Breadcrumbs,
	createResource,
	FormControl,
	usePageMeta,
} from 'frappe-ui'
import { Laptop, Plus, Search } from 'lucide-vue-next'
import { sessionStore } from '../stores/session'
import { inject, computed, ref, onMounted } from 'vue'
import JobCard from '@/components/JobCard.vue'

const user = inject('$user')
const jobType = ref(null)
const { brand } = sessionStore()
const searchQuery = ref('')
const filters = ref({})
const orFilters = ref({})

onMounted(() => {
	let queries = new URLSearchParams(location.search)
	if (queries.has('type')) {
		jobType.value = queries.get('type')
	}
	updateJobs()
})

const jobs = createResource({
	url: 'dls.dls.api.get_job_opportunities',
	cache: ['jobs'],
})

const updateJobs = () => {
	updateFilters()
	jobs.update({
		params: {
			filters: filters.value,
			orFilters: orFilters.value,
		},
	})
	jobs.reload()
}

const updateFilters = () => {
	filters.value.status = 'Open'
	filters.value.disabled = 0

	if (jobType.value) {
		filters.value.type = jobType.value
	} else {
		delete filters.value.type
	}

	if (searchQuery.value) {
		orFilters.value = {
			job_title: ['like', `%${searchQuery.value}%`],
			company_name: ['like', `%${searchQuery.value}%`],
			location: ['like', `%${searchQuery.value}%`],
		}
	} else {
		orFilters.value = {}
	}
}

const jobTypes = computed(() => {
	return [
		'',
		{ label: __('Full Time'), value: 'Full Time' },
		{ label: __('Part Time'), value: 'Part Time' },
		{ label: __('Contract'), value: 'Contract' },
		{ label: __('Freelance'), value: 'Freelance' },
	]
})

usePageMeta(() => {
	return {
		title: __('Jobs'),
		icon: brand.favicon,
	}
})
</script>
