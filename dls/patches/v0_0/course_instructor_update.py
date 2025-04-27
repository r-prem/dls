import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_course")
	courses = frappe.get_all("DLS Course", fields=["name", "owner"])
	for course in courses:
		frappe.db.set_value("DLS Course", course.name, "instructor", course.owner)
