import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_certification")
	certificates = frappe.get_all("LMS Certification", fields=["name", "student"])
	for certificate in certificates:
		frappe.db.set_value(
			"LMS Certification", certificate.name, "member", certificate.student
		)
