import frappe
from dls.dls.utils import get_course_progress


def execute():
	enrollments = frappe.get_all("DLS Enrollment", fields=["name", "course", "member"])

	for enrollment in enrollments:
		progress = get_course_progress(enrollment.course, enrollment.member)
		frappe.db.set_value("DLS Enrollment", enrollment.name, "progress", progress)
