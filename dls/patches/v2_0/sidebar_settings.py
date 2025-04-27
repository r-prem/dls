import frappe


def execute():
	fields = [
		"courses",
		"batches",
		"certified_participants",
		"jobs",
		"statistics",
		"notifications",
	]

	for field in fields:
		frappe.db.set_single_value("DLS Settings", field, 1)
