import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_batch")
	batches = frappe.get_all("DLS Batch", pluck="name")

	for batch in batches:
		frappe.db.set_value("DLS Batch", batch, "Published", 1)
