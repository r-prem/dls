import frappe
from dls.install import create_batch_source


def execute():
	frappe.reload_doc("lms", "doctype", "lms_source")
	create_batch_source()
