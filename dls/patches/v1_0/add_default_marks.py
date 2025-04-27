import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_quiz_question")
	frappe.reload_doc("dls", "doctype", "dls_quiz")
	questions = frappe.get_all("DLS Quiz Question", pluck="name")

	for question in questions:
		frappe.db.set_value("DLS Quiz Question", question, "marks", 1)

	quizzes = frappe.get_all("DLS Quiz", pluck="name")

	for quiz in quizzes:
		questions_count = frappe.db.count("DLS Quiz Question", {"parent": quiz})
		frappe.db.set_value(
			"DLS Quiz", quiz, {"total_marks": questions_count, "passing_percentage": 100}
		)
