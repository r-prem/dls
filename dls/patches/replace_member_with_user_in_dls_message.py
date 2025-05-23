import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_message")
	messages = frappe.get_all("DLS Message", ["author", "name"])
	for message in messages:
		user = frappe.db.get_value(
			"Community Member", message.author, ["email", "full_name"], as_dict=True
		)
		frappe.db.set_value("DLS Message", message.name, "author", user.email)
		frappe.db.set_value("DLS Message", message.name, "author_name", user.full_name)
