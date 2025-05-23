<template>
	<div class="flex flex-col min-h-0">
		<div class="flex items-center justify-between">
			<div class="text-xl font-semibold mb-5 text-ink-gray-9">
				{{ __('Categories') }}
			</div>
			<Button @click="() => showCategoryForm()">
				<template #icon>
					<Plus v-if="!showForm" class="h-3 w-3 stroke-1.5" />
					<X v-else class="h-3 w-3 stroke-1.5" />
				</template>
			</Button>
		</div>

		<div
			v-if="showForm"
			class="flex items-center justify-between my-4 space-x-2"
		>
			<FormControl
				ref="categoryInput"
				v-model="category"
				:placeholder="__('Category Name')"
				class="flex-1"
			/>
			<Button @click="addCategory()" variant="subtle">
				{{ __('Add') }}
			</Button>
		</div>

		<div class="overflow-y-scroll">
			<div class="text-base space-y-2">
				<div class="flex items-center space-x-2" v-for="cat in categories.data">
					<FormControl
						:value="cat.category"
						type="text"
						class="flex-1"
						@change.stop="(e) => update(cat.name, e.target.value)"
					/>
					<Button
						@click="() => deleteCategory(cat.name)"
						variant="ghost"
						class="text-red-500 hover:text-red-600"
					>
						<template #icon>
							<Trash2 class="h-4 w-4" />
						</template>
					</Button>
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import {
	Button,
	FormControl,
	createListResource,
	createResource,
	debounce,
} from 'frappe-ui'
import { Plus, X, Trash2 } from 'lucide-vue-next'
import { ref } from 'vue'

const showForm = ref(false)
const category = ref(null)
const categoryInput = ref(null)

const props = defineProps({
	label: {
		type: String,
		required: true,
	},
	description: {
		type: String,
		default: '',
	},
})

const categories = createListResource({
	doctype: 'DLS Category',
	fields: ['name', 'category'],
	auto: true,
})

const newCategory = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'DLS Category',
				category: category.value,
			},
		}
	},
})

const deleteCategoryResource = createResource({
	url: 'frappe.client.delete',
	makeParams(values) {
		return {
			doctype: 'DLS Category',
			name: values.name,
		}
	},
})

const deleteCategory = (name) => {
	deleteCategoryResource.submit(
		{
			name: name,
		},
		{
			onSuccess() {
				categories.reload()
			},
		}
	)
}

const addCategory = () => {
	newCategory.submit(
		{},
		{
			onSuccess(data) {
				categories.reload()
				category.value = null
			},
		}
	)
}

const showCategoryForm = () => {
	showForm.value = !showForm.value
	setTimeout(() => {
		categoryInput.value.$el.querySelector('input').focus()
	}, 0)
}

const updateCategory = createResource({
	url: 'frappe.client.rename_doc',
	makeParams(values) {
		return {
			doctype: 'DLS Category',
			old_name: values.name,
			new_name: values.category,
		}
	},
})

const update = (name, value) => {
	updateCategory.submit(
		{
			name: name,
			category: value,
		},
		{
			onSuccess() {
				categories.reload()
			},
		}
	)
}
</script>
