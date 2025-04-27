import frappe
from frappe.utils import ceil, flt


def execute():
	quizzes = frappe.get_all(
		"DLS Quiz", fields=["name", "duration"], filters={"duration": [">", 0]}
	)
	for quiz in quizzes:
		frappe.db.set_value("DLS Quiz", quiz.name, "duration", ceil(flt(quiz.duration) / 60))
