import frappe


def execute():
	frappe.db.delete("Web Form", {"module": "DLS", "is_standard": 1})
