import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_mentor_request")
	requests = frappe.get_all("DLS Mentor Request", ["member", "name"])
	for request in requests:
		user = frappe.db.get_value(
			"Community Member", request.member, ["email", "full_name"], as_dict=True
		)
		frappe.db.set_value("DLS Mentor Request", request.name, "member", user.email)
		frappe.db.set_value("DLS Mentor Request", request.name, "member_name", user.full_name)
