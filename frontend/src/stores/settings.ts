lessonCompletionTime: createDocumentResource({
  doctype: 'Single',
  name: 'DLS Settings',
  fields: ['lesson_completion_time'],
  transform(data) {
    return data.lesson_completion_time || 30 // fallback to 30 seconds if not set
  }
}),
