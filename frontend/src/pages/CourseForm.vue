<template>
	<div class="h-full">
		<div class="grid md:grid-cols-[70%,30%] h-full">
			<div>
				<header
					class="sticky top-0 z-10 flex flex-col md:flex-row md:items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
				>
					<Breadcrumbs class="h-7" :items="breadcrumbs" />
					<div class="flex items-center mt-3 md:mt-0">
						<Button v-if="courseResource.data?.name" @click="trashCourse()">
							<template #icon>
								<Trash2 class="w-4 h-4 stroke-1.5" />
							</template>
						</Button>
						<Button variant="solid" @click="submitCourse()" class="ml-2">
							<span>
								{{ __('Save') }}
							</span>
						</Button>
					</div>
				</header>
				<div class="mt-5 mb-10">
					<div class="container mb-5">
						<div class="text-lg font-semibold mb-4">
							{{ __('Details') }}
						</div>
						<FormControl
							v-model="course.title"
							:label="__('Title')"
							class="mb-4"
							:required="true"
						/>
						<FormControl
							v-model="course.short_introduction"
							:label="__('Short Introduction')"
							:placeholder="
								__(
									'A one line introduction to the course that appears on the course card'
								)
							"
							class="mb-4"
							:required="true"
						/>
						<div class="mb-4">
							<div class="mb-1.5 text-sm text-ink-gray-5">
								{{ __('Course Description') }}
								<span class="text-ink-red-3">*</span>
							</div>
							<TextEditor
								:content="course.description"
								@change="(val) => (course.description = val)"
								:editable="true"
								:fixedMenu="true"
								editorClass="prose-sm max-w-none border-b border-x bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
							/>
						</div>
						<div class="mb-4">
							<div class="text-xs text-ink-gray-5 mb-2">
								{{ __('Course Image') }}
								<span class="text-ink-red-3">*</span>
							</div>
							<FileUploader
								v-if="!course.course_image"
								:fileTypes="['image/*']"
								:validateFile="validateFile"
								@success="(file) => saveImage(file)"
							>
								<template
									v-slot="{ file, progress, uploading, openFileSelector }"
								>
									<div class="flex items-center">
										<div class="border rounded-md w-fit py-5 px-20">
											<Image class="size-5 stroke-1 text-ink-gray-7" />
										</div>
										<div class="ml-4">
											<Button @click="openFileSelector">
												{{ __('Upload') }}
											</Button>
											<div class="mt-2 text-ink-gray-5 text-sm">
												{{
													__('Appears on the course card in the course list')
												}}
											</div>
										</div>
									</div>
								</template>
							</FileUploader>
							<div v-else class="mb-4">
								<div class="flex items-center">
									<img
										:src="course.course_image.file_url"
										class="border rounded-md w-40"
									/>
									<div class="ml-4">
										<Button @click="removeImage()">
											{{ __('Remove') }}
										</Button>
										<div class="mt-2 text-ink-gray-5 text-sm">
											{{ __('Appears on the course card in the course list') }}
										</div>
									</div>
								</div>
							</div>
						</div>
						<div class="w-1/2 mb-4">
							<Link
								doctype="DLS Category"
								v-model="course.category"
								:label="__('Category')"
								:onCreate="(value, close) => openSettings(close)"
							/>
						</div>
					</div>
					<div class="container border-t">
						<div class="text-lg font-semibold mt-5 mb-4">
							{{ __('Settings') }}
						</div>
						<div class="grid grid-cols-2 gap-10 mb-4">
							<div
								v-if="user.data?.is_moderator"
								class="flex flex-col space-y-4"
							>
								<FormControl
									type="checkbox"
									v-model="course.published"
									:label="__('Published')"
								/>
								<FormControl
									v-model="course.published_on"
									:label="__('Published On')"
									type="date"
									class="mb-5"
								/>
							</div>
							<div class="flex flex-col space-y-3">
								<FormControl
									type="checkbox"
									v-model="course.upcoming"
									:label="__('Upcoming')"
								/>
								<FormControl
									type="checkbox"
									v-model="course.featured"
									:label="__('Featured')"
								/>
								<FormControl
									type="checkbox"
									v-model="course.disable_self_learning"
									:label="__('Disable Self Enrollment')"
									class="hidden"
								/>
								<FormControl
									v-if="settingsStore.certificatesEnabled.data"
									type="checkbox"
									v-model="course.enable_certification"
									:label="__('Completion Certificate')"
								/>
							</div>
						</div>
					</div>
					<div class="container border-t space-y-4" v-if="settingsStore.paidCoursesEnabled.data">
						<div class="text-lg font-semibold mt-5">
							{{ __('Pricing and Certification') }}
						</div>
						<div class="grid grid-cols-3">
							<FormControl
								type="checkbox"
								v-model="course.paid_course"
								:label="__('Paid Course')"
							/>
							<FormControl
								type="checkbox"
								v-model="course.paid_certificate"
								:label="__('Paid Certificate')"
							/>
						</div>
						<FormControl v-model="course.course_price" :label="__('Amount')" />
						<Link
							doctype="Currency"
							v-model="course.currency"
							:filters="{ enabled: 1 }"
							:label="__('Currency')"
						/>
						<Link
							v-if="course.paid_certificate"
							doctype="Course Evaluator"
							v-model="course.evaluator"
							:label="__('Evaluator')"
						/>
					</div>
				</div>
			</div>
			<div class="border-l">
				<CourseOutline
					v-if="courseResource.data"
					:courseName="courseResource.data.name"
					:title="__('Course Outline')"
					:allowEdit="true"
				/>
			</div>
		</div>
	</div>
</template>
<script setup>
import {
	Breadcrumbs,
	TextEditor,
	Button,
	createResource,
	FormControl,
	FileUploader,
	usePageMeta,
} from 'frappe-ui'
import {
	inject,
	onMounted,
	onBeforeUnmount,
	computed,
	ref,
	reactive,
	watch,
	getCurrentInstance,
} from 'vue'
import { showToast } from '@/utils'
import { Image, Trash2, X } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { capture } from '@/telemetry'
import { useOnboarding } from 'frappe-ui/frappe'
import { sessionStore } from '../stores/session'
import { useSettings } from '@/stores/settings'
import Link from '@/components/Controls/Link.vue'
import CourseOutline from '@/components/CourseOutline.vue'
import MultiSelect from '@/components/Controls/MultiSelect.vue'

const user = inject('$user')
const newTag = ref('')
const { brand } = sessionStore()
const router = useRouter()
const settingsStore = useSettings()
const app = getCurrentInstance()
const { updateOnboardingStep } = useOnboarding('learning')
const { $dialog } = app.appContext.config.globalProperties

const instructors = ref([])

const props = defineProps({
	courseName: {
		type: String,
	},
})

const course = reactive({
	title: '',
	short_introduction: '',
	description: '',
	video_link: '',
	course_image: null,
	tags: '',
	category: '',
	published: false,
	published_on: '',
	featured: false,
	upcoming: false,
	disable_self_learning: false,
	enable_certification: false,
	paid_course: false,
	paid_certificate: false,
	course_price: '',
	currency: '',
	evaluator: '',
	instructors: [],
})

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) {
		router.push({ name: 'Courses' })
	}

	if (props.courseName !== 'new') {
		courseResource.reload()
	} else {
		capture('course_form_opened')
	}
	window.addEventListener('keydown', keyboardShortcut)
})

const keyboardShortcut = (e) => {
	if (
		e.key === 's' &&
		(e.ctrlKey || e.metaKey) &&
		!e.target.classList.contains('ProseMirror')
	) {
		submitCourse()
		e.preventDefault()
	}
}

onBeforeUnmount(() => {
	window.removeEventListener('keydown', keyboardShortcut)
})

const courseCreationResource = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'DLS Course',
				image: course.course_image?.file_url || '',
				instructors: [{
					instructor: user.data?.name
				}],
				...values,
			},
		}
	},
})

const courseEditResource = createResource({
	url: 'frappe.client.set_value',
	auto: false,
	makeParams(values) {
		return {
			doctype: 'DLS Course',
			name: values.course,
			fieldname: {
				...course,
				image: course.course_image?.file_url || '',
				instructors: [{
					instructor: user.data?.name
				}],

			},
		}
	},
})

const courseResource = createResource({
	url: 'frappe.client.get',
	makeParams(values) {
		return {
			doctype: 'DLS Course',
			name: props.courseName,
		}
	},
	auto: false,
	onSuccess(data) {
		Object.keys(data).forEach((key) => {
			if (key == 'instructors' && data.instructors && data.instructors.value) {
				instructors.value = []
				data.instructors.forEach((instructor) => {
					instructors.value.push(instructor.instructor)
				})
			} else if (Object.hasOwn(course, key)) course[key] = data[key]
		})
		let checkboxes = [
			'published',
			'upcoming',
			'disable_self_learning',
			'paid_course',
			'featured',
			'enable_certification',
			'paid_certificate',
		]
		for (let idx in checkboxes) {
			let key = checkboxes[idx]
			course[key] = course[key] ? true : false
		}
		if (data.image) imageResource.reload({ image: data.image })
		check_permission()
	},
})

const imageResource = createResource({
	url: 'dls.dls.api.get_file_info',
	makeParams(values) {
		return {
			file_url: values.image,
		}
	},
	auto: false,
	onSuccess(data) {
		course.course_image = data
	},
})

const submitCourse = () => {
	if (courseResource.data) {
		courseEditResource.submit(
			{
				course: courseResource.data.name,
			},
			{
				onSuccess() {
					showToast('Success', 'Course updated successfully', 'check')
				},
				onError(err) {
					showToast('Error', err.messages?.[0] || err, 'x')
				},
			}
		)
	} else {
		courseCreationResource.submit(course, {
			onSuccess(data) {
				if (user.data?.is_system_manager) {
					updateOnboardingStep('create_first_course', true, false, () => {
						localStorage.setItem('firstCourse', data.name)
					})
				}

				capture('course_created')
				showToast('Success', 'Course created successfully', 'check')
				router.push({
					name: 'CourseForm',
					params: { courseName: data.name },
				})
			},
			onError(err) {
				showToast('Error', err.messages?.[0] || err, 'x')
			},
		})
	}
}

const deleteCourse = createResource({
	url: 'dls.dls.api.delete_course',
	makeParams(values) {
		return {
			course: props.courseName,
		}
	},
	onSuccess() {
		showToast(__('Success'), __('Course deleted successfully'), 'check')
		router.push({ name: 'Courses' })
	},
})

const trashCourse = () => {
	$dialog({
		title: __('Delete Course'),
		message: __(
			'Deleting the course will also delete all its chapters and lessons. Are you sure you want to delete this course?'
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					deleteCourse.submit()
					close()
				},
			},
		],
	})
}

watch(
	() => props.courseName !== 'new',
	(newVal) => {
		if (newVal) {
			courseResource.reload()
		}
	}
)

const validateFile = (file) => {
	let extension = file.name.split('.').pop().toLowerCase()
	if (!['jpg', 'jpeg', 'png', 'webp'].includes(extension)) {
		return __('Only image file is allowed.')
	}
}

const updateTags = () => {
	if (newTag.value) {
		course.tags = course.tags ? `${course.tags}, ${newTag.value}` : newTag.value
		newTag.value = ''
	}
}

const removeTag = (tag) => {
	course.tags = course.tags
		?.split(', ')
		.filter((t) => t !== tag)
		.join(', ')
	newTag.value = ''
}

const saveImage = (file) => {
	course.course_image = file
}

const removeImage = () => {
	course.course_image = null
}

const openSettings = (close) => {
	close()
	settingsStore.activeTab = 'Categories'
	settingsStore.isSettingsOpen = true
}

const check_permission = () => {
	let user_is_instructor = false
	if (user.data?.is_moderator) return

	instructors.value.forEach((instructor) => {
		if (!user_is_instructor && instructor == user.data?.name) {
			user_is_instructor = true
		}
	})

	if (!user_is_instructor) {
		router.push({ name: 'Courses' })
	}
}

const breadcrumbs = computed(() => {
	let crumbs = [
		{
			label: 'Courses',
			route: { name: 'Courses' },
		},
	]
	if (courseResource.data) {
		crumbs.push({
			label: course.title,
			route: { name: 'CourseDetail', params: { courseName: props.courseName } },
		})
	}
	crumbs.push({
		label: props.courseName == 'new' ? 'New Course' : 'Edit Course',
		route: { name: 'CourseForm', params: { courseName: props.courseName } },
	})
	return crumbs
})

usePageMeta(() => {
	return {
		title: courseResource.data?.title || __('New Course'),
		icon: brand.favicon,
	}
})
</script>
