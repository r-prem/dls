import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_course_progress")
	progress_records = frappe.get_all(
		"DLS Course Progress", fields=["name", "owner", "member"]
	)

	for progress in progress_records:
		if not progress.member:
			full_name = frappe.db.get_value("User", progress.owner, "full_name")
			frappe.db.set_value("DLS Course Progress", progress.name, "member", progress.owner)
			frappe.db.set_value("DLS Course Progress", progress.name, "member_name", full_name)
