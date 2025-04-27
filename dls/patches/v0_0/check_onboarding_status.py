import frappe


def execute():
	if (
		frappe.db.count("DLS Course")
		and frappe.db.count("Course Chapter")
		and frappe.db.count("Course Lesson")
		and frappe.db.count("DLS Quiz")
	):
		frappe.db.set_value("DLS Settings", None, "is_onboarding_complete", True)
