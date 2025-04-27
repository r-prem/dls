import frappe
from dls.install import create_batch_source


def execute():
	frappe.reload_doc("dls", "doctype", "dls_source")
	create_batch_source()
