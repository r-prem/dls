<template>
  <div>
    <header class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5">
      <Breadcrumbs :items="breadcrumbs" />
    </header>
    <div class="p-5">
      <div class="flex items-center justify-between mb-6">
        <div class="text-xl font-semibold">{{ __('Course Completions') }}</div>
        <div class="flex space-x-4">
          <FormControl
            v-model="selectedCourse"
            type="select"
            :options="formattedCourseOptions"
            :placeholder="__('Select Course')"
            @change="loadCompletions"
          />
        </div>
      </div>

      <div v-if="completions.data?.length" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="border rounded-lg p-4">
            <div class="text-sm text-gray-600">{{ __('Total Enrolled') }}</div>
            <div class="text-2xl font-semibold mt-1">{{ totalEnrolled }}</div>
          </div>
          <div class="border rounded-lg p-4">
            <div class="text-sm text-gray-600">{{ __('Completed') }}</div>
            <div class="text-2xl font-semibold mt-1">{{ completedCount }}</div>
          </div>
          <div class="border rounded-lg p-4">
            <div class="text-sm text-gray-600">{{ __('Completion Rate') }}</div>
            <div class="text-2xl font-semibold mt-1">{{ completionRate }}%</div>
          </div>
        </div>

        <ListView
          :columns="columns"
          :rows="sortedCompletions"
          row-key="name"
          :options="{ 
            showTooltip: false,
            sortBy: sortBy,
            sortOrder: sortOrder
          }"
          @sort="({ sortBy: newSortBy, sortOrder: newSortOrder }) => {
            sortBy.value = newSortBy
            sortOrder.value = newSortOrder
          }"
        >
          <ListHeader class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2">
            <ListHeaderItem :item="item" v-for="item in columns" />
          </ListHeader>
          <ListRows>
            <ListRow :row="row" v-for="row in sortedCompletions">
              <template #default="{ column, item }">
                <ListRowItem :item="row[column.key]" :align="column.align">
                  <template #prefix v-if="column.key === 'member_name'">
                    <Avatar
                      class="flex items-center"
                      :image="row.user_image"
                      :label="row.member_name"
                      size="sm"
                    />
                  </template>
                  <div v-if="column.key === 'progress'" class="flex items-center">
                    {{ row.progress }}%
                  </div>
                  <div v-else-if="column.key === 'modified'">
                    {{ formatDate(row.modified) }}
                  </div>
                  <div v-else>
                    {{ row[column.key] }}
                  </div>
                </ListRowItem>
              </template>
            </ListRow>
          </ListRows>
        </ListView>
      </div>
      <div v-else-if="completions.loading" class="flex items-center justify-center mt-8">
        <LoadingIndicator class="h-8 w-8" />
      </div>
      <div v-else-if="selectedCourse" class="text-center text-gray-600 mt-8">
        {{ __('No completion data available for this course') }}
      </div>
      <div v-else class="text-center text-gray-600 mt-8">
        {{ __('Select a course to view completion data') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Avatar,
  Breadcrumbs,
  FormControl,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRows,
  ListRow,
  ListRowItem,
  createResource,
  usePageMeta,
  LoadingIndicator
} from 'frappe-ui'
import { ref, computed, inject, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ProgressBar from '@/components/ProgressBar.vue'
import { sessionStore } from '@/stores/session'

const router = useRouter()
const user = inject('$user')
const { brand } = sessionStore()
const selectedCourse = ref('')

onMounted(() => {
  if (!user.data?.is_moderator && !user.data?.is_system_manager) {
    router.push({ name: 'Courses' })
  }
})

const courses = createResource({
  url: 'lms.lms.utils.get_courses',
  params: {
    filters: {
      published: 1
    }
  },
  auto: true,
  onSuccess(data) {
    console.log('Courses data:', data)
  },
  onError(error) {
    console.error('Error fetching courses:', error)
  }
})

const formattedCourseOptions = computed(() => {
  return courses.data?.map(course => ({
    label: course.title,
    value: course.name
  })) || []
})

const completions = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'LMS Enrollment',
    fields: ['name', 'member', 'member_name', 'progress', 'creation', 'modified'],
    filters: { course: selectedCourse.value },
    order_by: 'progress desc'
  }
})

const loadCompletions = () => {
  if (selectedCourse.value) {
    completions.update({
      params: {
        doctype: 'LMS Enrollment',
        fields: ['name', 'member', 'member_name', 'progress', 'creation', 'modified'],
        filters: { course: selectedCourse.value }
      }
    })
    completions.reload()
  }
}

const columns = [
  {
    label: 'Student',
    key: 'member_name',
    sortable: true
  },
  {
    label: 'Progress',
    key: 'progress',
    sortable: true
  },
  {
    label: 'Last Updated',
    key: 'modified',
    align: 'right',
    sortable: true
  }
]

const sortBy = ref('modified')
const sortOrder = ref('desc')

const sortedCompletions = computed(() => {
  if (!completions.data) return []
  
  return [...completions.data].sort((a, b) => {
    const aValue = a[sortBy.value]
    const bValue = b[sortBy.value]
    
    if (sortBy.value === 'progress') {
      return sortOrder.value === 'desc' ? bValue - aValue : aValue - bValue
    }
    
    if (sortOrder.value === 'desc') {
      return bValue > aValue ? 1 : -1
    }
    return aValue > bValue ? 1 : -1
  })
})

const totalEnrolled = computed(() => completions.data?.length || 0)
const completedCount = computed(() => completions.data?.filter(c => c.progress === 100)?.length || 0)
const completionRate = computed(() => {
  if (!totalEnrolled.value) return 0
  return Math.round((completedCount.value / totalEnrolled.value) * 100)
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const breadcrumbs = computed(() => [
  {
    label: 'Courses',
    route: { name: 'Courses' }
  },
  {
    label: 'Course Completions',
    route: { name: 'CourseCompletions' }
  }
])

usePageMeta(() => ({
  title: 'Course Completions',
  icon: brand.favicon
}))
</script> 