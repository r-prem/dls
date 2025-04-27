import frappe
from frappe.model.rename_doc import rename_doc


def execute():
	if frappe.db.exists("DocType", "DLS Enrollment"):
		return

	frappe.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "DLS Batch Membership", "DLS Enrollment")
	frappe.flags.ignore_route_conflict_validation = False

	frappe.reload_doctype("DLS Enrollment", force=True)
