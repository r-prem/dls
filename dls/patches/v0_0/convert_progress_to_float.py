import frappe
from frappe.utils import flt


def execute():
	frappe.reload_doc("dls", "doctype", "dls_course_progress")
	progress_records = frappe.get_all("LMS Enrollment", fields=["name", "progress"])
	for progress in progress_records:
		frappe.db.set_value(
			"LMS Enrollment", progress.name, "progress", flt(progress.progress)
		)
