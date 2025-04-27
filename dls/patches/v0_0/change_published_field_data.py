import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_course")
	courses = frappe.get_all("DLS Course", fields=["name", "is_published"])
	for course in courses:
		frappe.db.set_value("DLS Course", course.name, "published", course.is_published)
