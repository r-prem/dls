import frappe
from dls.dls.md import markdown_to_html


def execute():
	courses = frappe.get_all("DLS Course", fields=["name", "description"])

	for course in courses:
		html = markdown_to_html(course.description)
		frappe.db.set_value("DLS Course", course.name, "description", html)

	frappe.reload_doc("dls", "doctype", "dls_course")
