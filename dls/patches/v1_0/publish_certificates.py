import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_certificate")
	certificates = frappe.get_all("DLS Certificate", pluck="name")

	for certificate in certificates:
		frappe.db.set_value("DLS Certificate", certificate, "published", 1)
