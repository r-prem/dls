<template>
	<div class="flex flex-col justify-between min-h-0">
		<div>
			<div class="flex items-center justify-between">
				<div class="font-semibold mb-1 text-ink-gray-9">
					{{ __(label) }}
				</div>
				<Badge
					v-if="isDirty"
					:label="__('Not Saved')"
					variant="subtle"
					theme="orange"
				/>
			</div>
			<div class="text-xs text-ink-gray-5">
				{{ __(description) }}
			</div>
		</div>
		<div class="overflow-y-auto">
			<SettingFields :fields="fields" :data="localData" />
			<div class="flex flex-row-reverse mt-auto">
				<Button variant="solid" :loading="saveSettings.loading" @click="update">
					{{ __('Update') }}
				</Button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { createResource, Button, Badge } from 'frappe-ui'
import SettingFields from '@/components/SettingFields.vue'
import { watch, ref, defineEmits, reactive } from 'vue'
import { generateColorRange, injectPrimaryColorVariables } from '@/utils/colors'

const isDirty = ref(false)
const emit = defineEmits(['saved'])

const props = defineProps({
	fields: {
		type: Array,
		required: true,
	},
	data: {
		type: Object,
		required: true,
	},
	label: {
		type: String,
		required: true,
	},
	description: {
		type: String,
	},
})

const saveSettings = createResource({
	url: 'frappe.client.set_value',
	makeParams(values) {
		return {
			doctype: 'Website Settings',
			name: 'Website Settings',
			fieldname: values.fields,
		}
	},
})

// Create a local copy of the data for editing
const localData = reactive({ ...props.data.data })

// Watch for changes in props.data.data (e.g., when modal is opened)
watch(
	() => props.data.data,
	(newData) => {
		Object.assign(localData, newData)
	},
	{ immediate: true, deep: true }
)

const update = () => {
	let fieldsToSave = {}
	let imageFields = ['favicon', 'banner_image', 'footer_logo']
	props.fields.forEach((f) => {
		if (imageFields.includes(f.name)) {
			fieldsToSave[f.name] = localData[f.name] ? localData[f.name].file_url : null
		} else {
			fieldsToSave[f.name] = localData[f.name]
		}
	})

	saveSettings.submit(
		{
			fields: fieldsToSave,
		},
		{
			onSuccess(data) {
				isDirty.value = false
				emit('saved', fieldsToSave.primary_color)
				// Inject CSS variables only after successful save
				if (fieldsToSave.primary_color) {
					injectPrimaryColorVariables(fieldsToSave.primary_color)
				}
			}
		}
	)
}

watch(props.data, (newData) => {
	if (newData && !isDirty.value) {
		isDirty.value = true
	}

	// Inject primary color CSS variables on initial load
	if (newData && newData.primary_color) {
		injectPrimaryColorVariables(newData.primary_color)
	}

	// If primary color is being updated, generate and apply the color range
	if (fieldsToSave.primary_color) {
		injectPrimaryColorVariables(fieldsToSave.primary_color)
	}
})
</script>
