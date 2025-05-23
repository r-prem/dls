<template>
	<Dialog v-model="show" :options="{ size: '4xl' }">

		<template #body>

			<div class="flex h-[calc(100vh_-_8rem)]">
				<div class="flex w-52 shrink-0 flex-col bg-surface-gray-2 p-2">
					<h1 class="mb-3 px-2 pt-2 text-lg font-semibold text-ink-gray-9">
						{{ __('Settings') }}
					</h1>
					<div v-for="tab in tabs" :key="tab.label">
						<div
							v-if="!tab.hideLabel"
							class="mb-2 mt-3 flex cursor-pointer gap-1.5 px-1 text-base font-medium text-ink-gray-5 transition-all duration-300 ease-in-out"
						>
							<span>{{ __(tab.label) }}</span>
						</div>
						<nav class="space-y-1">
							<SidebarLink
								v-for="item in tab.items"
								:link="item"
								:key="item.label"
								class="w-full"
								:class="
									activeTab?.label == item.label
										? 'bg-surface-selected shadow-sm'
										: 'hover:bg-surface-gray-2'
								"
								@click="activeTab = item"
							/>
						</nav>
					</div>
				</div>
				<div
					v-if="activeTab && data.doc"
					:key="activeTab.label"
					class="flex flex-1 flex-col px-10 py-8 bg-surface-modal"
				>
					<Members
						v-if="activeTab.label === 'Members'"
						:label="activeTab.label"
						:description="activeTab.description"
						v-model:show="show"
					/>
					<Evaluators
						v-else-if="activeTab.label === 'Evaluators'"
						:label="activeTab.label"
						:description="activeTab.description"
						v-model:show="show"
					/>
					<Categories
						v-else-if="activeTab.label === 'Categories'"
						:label="activeTab.label"
						:description="activeTab.description"
					/>
					<PaymentSettings
						v-else-if="activeTab.label === 'Payment Gateway'"
						:label="activeTab.label"
						:description="activeTab.description"
						:data="data"
						:fields="activeTab.fields"
					/>
					<BrandSettings
						v-else-if="activeTab.label === 'Branding'"
						:label="activeTab.label"
						:description="activeTab.description"
						:fields="activeTab.fields"
						:data="branding"
						@saved="onBrandingSaved"
					/>
					<SettingDetails
						v-else
						:fields="activeTab.fields"
						:label="activeTab.label"
						:description="activeTab.description"
						:data="data"
					/>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup>
import { Dialog, createDocumentResource, createResource } from 'frappe-ui'
import { ref, computed, watch, nextTick } from 'vue'
import { useSettings } from '@/stores/settings'
import SettingDetails from '../SettingDetails.vue'
import SidebarLink from '@/components/SidebarLink.vue'
import Members from '@/components/Members.vue'
import Evaluators from '@/components/Evaluators.vue'
import Categories from '@/components/Categories.vue'
import BrandSettings from '@/components/BrandSettings.vue'
import PaymentSettings from '@/components/PaymentSettings.vue'
import { generateColorRange } from '@/utils/colors'

const show = defineModel()
const doctype = ref('DLS Settings')
const activeTab = ref(null)
const settingsStore = useSettings()

const data = createDocumentResource({
	doctype: doctype.value,
	name: doctype.value,
	fields: ['*'],
	cache: doctype.value,
	auto: true,
})

const branding = createResource({
	url: 'dls.dls.api.get_branding',
	auto: true,
	cache: 'brand',
})

let originalPrimaryColor = null
let isBrandingSaved = false

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
		button.bg-surface-gray-7,
		div.bg-surface-gray-7.rounded-full.h-1 {
			${Object.entries(colors).map(([key, value]) => `${key}: ${value};`).join('\n')}
		}
	`
}

watch(show, (val, oldVal) => {
	if (val && !oldVal) {
		originalPrimaryColor = branding.data?.primary_color
		isBrandingSaved = false
	} else if (!val && oldVal) {
		nextTick(() => {
			if (!isBrandingSaved) {
				injectPrimaryColorVariables(originalPrimaryColor)
			}
		})
	}
})

watch(activeTab, (newTab, oldTab) => {
	if (oldTab && oldTab.label === 'Branding' && newTab && newTab.label !== 'Branding') {
		nextTick(() => {
			if (!isBrandingSaved) {
				injectPrimaryColorVariables(originalPrimaryColor)
			}
		})
	}
})

function onBrandingSaved(newColor) {
	isBrandingSaved = true
}

const tabsStructure = computed(() => {
	const tabs = [
		{
			label: 'Settings',
			hideLabel: true,
			items: [
				{
					label: 'General',
					icon: 'Wrench',
					fields: [
						{
							label: 'Enable Learning Paths',
							name: 'enable_learning_paths',
							description: 'This will enforce students to go through programs assigned to them in the correct order.',
							type: 'checkbox',
						},
						{
							label: 'Allow Guest Access',
							name: 'allow_guest_access',
							description: 'If enabled, users can access the course and batch lists without logging in.',
							type: 'checkbox',
						},
						{
							label: 'Send calendar invite for evaluations',
							name: 'send_calendar_invite_for_evaluations',
							description: 'If enabled, it sends google calendar invite to the student for evaluations.',
							type: 'checkbox',
						},
						{
							label: 'Unsplash Access Key',
							name: 'unsplash_access_key',
							description: 'Optional. If this is set, students can pick a cover image from the unsplash library for their profile page. https://unsplash.com/documentation#getting-started.',
							type: 'password',
						},
						{
							label: 'OpenAI API Key',
							name: 'openai_api_key',
							description: 'Your OpenAI API key. You can get this from https://platform.openai.com/account/api-keys',
							type: 'password',
						},
					],
				},
				{
					label: 'Course Settings',
					icon: 'BookOpen',
					fields: [
						{
							label: 'Allow Course Ratings',
							name: 'ratings_allowed',
							description: 'If enabled, students can rate and review courses.',
							type: 'checkbox',
						},
						{
							label: 'Show Enrolled Students Count',
							name: 'show_enrolled_count',
							description: 'If enabled, the number of enrolled students will be displayed on course cards and pages.',
							type: 'checkbox',
						},
						{
							label: 'Enable Questions in Lessons',
							name: 'questions_active',
							description: 'If enabled, students can ask questions in the lesson page.',
							type: 'checkbox',
						},
						{
							label: 'Enable Paid Courses',
							name: 'enable_paid_courses',
							description: 'If enabled, courses can be set as paid courses with pricing.',
							type: 'checkbox',
						},
						{
							label: 'Display Instructor',
							name: 'display_instructor',
							description: 'If enabled, instructor information will be shown on course pages.',
							type: 'checkbox',
						},
						{
							label: 'Enable Certificates',
							name: 'enable_certificates',
							description: 'If disabled, certificates will not be available for courses.',
							type: 'checkbox',
						},
						{
							label: 'Enable Quizzes',
							name: 'enable_quizzes',
							description: 'If disabled, quizzes will not be available in lessons.',
							type: 'checkbox',
						},
						{
							label: 'Lesson Completion Time',
							name: 'lesson_completion_time',
							description: 'Time in seconds a user needs to spend on a lesson before it can be marked as complete.',
							type: 'number',
						},
					],
				},
			],
		},
		{
			label: 'Settings',
			hideLabel: true,
			items: [
				...(settingsStore.paidCoursesEnabled.data ? [
					{
						label: 'Payment Gateway',
						icon: 'DollarSign',
						description: 'Configure the payment gateway and other payment related settings',
						fields: [
							{
								label: 'Payment Gateway',
								name: 'payment_gateway',
								type: 'Link',
								doctype: 'Payment Gateway',
							},
							{
								label: 'Default Currency',
								name: 'default_currency',
								type: 'Link',
								doctype: 'Currency',
							},
							{
								label: 'Apply GST for India',
								name: 'apply_gst',
								type: 'checkbox',
							},
							{
								label: 'Show USD equivalent amount',
								name: 'show_usd_equivalent',
								type: 'checkbox',
							},
							{
								label: 'Apply rounding on equivalent',
								name: 'apply_rounding',
								type: 'checkbox',
							},
						],
					},
				] : []),
			],
		},
		{
			label: 'Lists',
			hideLabel: false,
			items: [
				{
					label: 'Members',
					description: 'Manage the members of your learning system',
					icon: 'UserRoundPlus',
				},
				{
					label: 'Evaluators',
					description: 'Manage the evaluators of your learning system',
					icon: 'UserCheck',
				},
				{
					label: 'Categories',
					description: 'Manage the members of your learning system',
					icon: 'Network',
				},
			],
		},
		{
			label: 'Customise',
			hideLabel: false,
			items: [
				{
					label: 'Branding',
					icon: 'Blocks',
					fields: [
						{
							label: 'Brand Name',
							name: 'app_name',
							type: 'text',
						},
						{
							label: 'Primary Color',
							name: 'primary_color',
							type: 'color',
							description: 'This will be used as the primary color for buttons and other UI elements'
						},
						{
							label: 'Logo',
							name: 'banner_image',
							type: 'Upload',
						},
						{
							label: 'Favicon',
							name: 'favicon',
							type: 'Upload',
						},
						{
							label: 'Footer Logo',
							name: 'footer_logo',
							type: 'Upload',
						},
						{
							label: 'Address',
							name: 'address',
							type: 'textarea',
							rows: 2,
						},
						{
							label: 'Footer "Powered By"',
							name: 'footer_powered',
							type: 'textarea',
							rows: 4,
						},
						{
							label: 'Copyright',
							name: 'copyright',
							type: 'text',
						},
					],
				},
				{
					label: 'Sidebar',
					icon: 'PanelLeftIcon',
					description: 'Choose the items you want to show in the sidebar',
					fields: [
						{
							label: 'Courses',
							name: 'courses',
							type: 'checkbox',
						},
						{
							label: 'Batches',
							name: 'batches',
							type: 'checkbox',
						},
						{
							label: 'Certified Participants',
							name: 'certified_participants',
							type: 'checkbox',
						},
						{
							label: 'Assignments',
							name: 'assignments',
							type: 'checkbox',
						},
						{
							type: 'Column Break',
						},
						{
							label: 'Jobs',
							name: 'jobs',
							type: 'checkbox',
						},
						{
							label: 'Statistics',
							name: 'statistics',
							type: 'checkbox',
						},
						{
							label: 'Notifications',
							name: 'notifications',
							type: 'checkbox',
						},
						{
							label: 'Programs',
							name: 'programs',
							type: 'checkbox',
						},
					],
				},
				{
					label: 'Email Templates',
					icon: 'MailPlus',
					fields: [
						{
							label: 'Batch Confirmation Template',
							name: 'batch_confirmation_template',
							doctype: 'Email Template',
							type: 'Link',
						},
						{
							label: 'Certification Template',
							name: 'certification_template',
							doctype: 'Email Template',
							type: 'Link',
						},
					],
				},
				{
					label: 'Signup',
					icon: 'LogIn',
					fields: [
						{
							label: 'Identify User Category',
							name: 'user_category',
							type: 'checkbox',
							description: 'Enable this option to identify the user category during signup.',
						},
						{
							label: 'Disable signup',
							name: 'disable_signup',
							type: 'checkbox',
							description: 'New users will have to be manually registered by Admins.',
						},
						{
							label: 'Signup Consent HTML',
							name: 'custom_signup_content',
							type: 'Code',
							mode: 'htmlmixed',
							rows: 10,
						},
					],
				},
				{
					label: 'SEO',
					icon: 'Search',
					fields: [
						{
							label: 'Meta Description',
							name: 'meta_description',
							type: 'textarea',
							rows: 4,
							description: "This description will be shown on lists and pages that don't have meta description",
						},
						{
							label: 'Meta Keywords',
							name: 'meta_keywords',
							type: 'textarea',
							rows: 4,
							description: 'Keywords for search engines to find your website. Separated by commas.',
						},
						{
							label: 'Meta Image',
							name: 'meta_image',
							type: 'Upload',
						},
					],
				},
			],
		},
	]
	return tabs
})

const tabs = computed(() => {
	return tabsStructure.value.map((tab) => {
		return {
			...tab,
			items: tab.items.filter((item) => {
				return !item.condition || item.condition()
			}),
		}
	})
})

watch(show, async () => {
	if (show.value) {
		const currentTab = await tabs.value
			.flatMap((tab) => tab.items)
			.find((item) => item.label === settingsStore.activeTab)
		activeTab.value = currentTab || tabs.value[0].items[0]
	} else {
		activeTab.value = null
		settingsStore.isSettingsOpen = false
	}
})
</script>
