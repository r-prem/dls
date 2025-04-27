import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_course")
	courses = frappe.get_all(
		"DLS Course",
		{"paid_certificate": ["is", "set"]},
		["name", "price_certificate", "currency"],
	)

	for course in courses:
		frappe.db.set_value(
			"DLS Course",
			course.name,
			{
				"paid_course": 1,
				"course_price": course.price_certificate,
				"currency": course.currency,
			},
		)
