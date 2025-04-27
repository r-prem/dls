import frappe


def execute():
	courses = frappe.get_all(
		"DLS Course", filters={"published": 1}, fields=["name", "creation"]
	)

	for course in courses:
		frappe.db.set_value("DLS Course", course.name, "published_on", course.creation)
