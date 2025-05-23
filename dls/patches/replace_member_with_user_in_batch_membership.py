import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_batch_membership")
	memberships = frappe.get_all("DLS Enrollment", ["member", "name"])
	for membership in memberships:
		email = frappe.db.get_value("Community Member", membership.member, "email")
		frappe.db.set_value("DLS Enrollment", membership.name, "member", email)
