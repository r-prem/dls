import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_certificate")
	default_certificate_template = frappe.db.get_value(
		"Property Setter",
		{
			"doc_type": "DLS Certificate",
			"property": "default_print_format",
		},
		"value",
	)

	if frappe.db.exists("Print Format", default_certificate_template):
		certificates = frappe.get_all("DLS Certificate", pluck="name")
		for certificate in certificates:
			frappe.db.set_value(
				"DLS Certificate", certificate, "template", default_certificate_template
			)
