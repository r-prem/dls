import frappe
from dls.install import create_dls_student_role


def execute():
	create_dls_student_role()

	users = frappe.get_all(
		"User", filters={"user_type": "Website User", "enabled": 1}, pluck="name"
	)

	for user in users:
		filters = {
			"parent": user,
			"parenttype": "User",
			"parentfield": "roles",
			"role": "DLS Student",
		}
		if not frappe.db.exists("Has Role", filters):
			doc = frappe.new_doc("Has Role")
			doc.update(filters)
			doc.save()
