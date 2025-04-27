import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_quiz_submission")
	frappe.reload_doc("dls", "doctype", "dls_quiz_result")
	results = frappe.get_all("LMS Quiz Result", fields=["name", "result"])

	for result in results:
		value = 1 if result.result == "Right" else 0
		frappe.db.set_value("LMS Quiz Result", result.name, "is_correct", value)
