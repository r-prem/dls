import frappe


def execute():
	frappe.db.set_single_value("DLS Settings", "allow_guest_access", 1)
