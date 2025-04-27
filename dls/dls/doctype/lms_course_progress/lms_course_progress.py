# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from dls.dls.utils import get_course_progress


class DLSCourseProgress(Document):
	def after_delete(self):
		progress = get_course_progress(self.course, self.member)
		membership = frappe.db.get_value(
			"DLS Enrollment",
			{
				"member": self.member,
				"course": self.course,
			},
			"name",
		)
		frappe.db.set_value("DLS Enrollment", membership, "progress", progress)
