import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_certification")
	frappe.reload_doc("dls", "doctype", "dls_certificate")
	old = frappe.get_all(
		"DLS Certification", fields=["name", "course", "student", "issue_date", "expiry_date"]
	)
	for data in old:
		frappe.get_doc(
			{
				"doctype": "DLS Certificate",
				"course": data.course,
				"member": data.student,
				"issue_date": data.issue_date,
				"expiry_date": data.expiry_date,
			}
		).insert(ignore_permissions=True, ignore_mandatory=True)
