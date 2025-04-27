import frappe
from frappe.model.rename_doc import rename_doc


def execute():
	if frappe.db.exists("DocType", "DLS Exercise"):
		return

	frappe.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Exercise", "DLS Exercise")
	frappe.flags.ignore_route_conflict_validation = False

	frappe.reload_doctype("DLS Exercise", force=True)
