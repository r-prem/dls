import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_quiz_question")
	questions = frappe.get_all("DLS Quiz Question", pluck="name")

	for question in questions:
		frappe.db.set_value("DLS Quiz Question", question, "type", "Choices")
