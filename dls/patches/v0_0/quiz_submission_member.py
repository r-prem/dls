import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_quiz_submission")
	submissions = frappe.db.get_all("DLS Quiz Submission", fields=["name", "owner"])

	for submission in submissions:
		frappe.db.set_value(
			"DLS Quiz Submission", submission.name, "member", submission.owner
		)
