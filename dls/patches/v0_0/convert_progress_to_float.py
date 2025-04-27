import frappe
from frappe.utils import flt


def execute():
	frappe.reload_doc("dls", "doctype", "dls_course_progress")
	progress_records = frappe.get_all("DLS Enrollment", fields=["name", "progress"])
	for progress in progress_records:
		frappe.db.set_value(
			"DLS Enrollment", progress.name, "progress", flt(progress.progress)
		)
