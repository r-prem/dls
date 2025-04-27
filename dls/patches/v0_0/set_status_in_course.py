import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_course")
	courses = frappe.get_all(
		"DLS Course", {"status": ("is", "not set")}, ["name", "published"]
	)
	for course in courses:
		status = "Approved" if course.published else "In Progress"
		frappe.db.set_value("DLS Course", course.name, "status", status)
