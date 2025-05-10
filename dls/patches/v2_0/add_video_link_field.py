import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    # Only add if it doesn't exist
    if not frappe.db.has_column("DLS Course", "video_link"):
        create_custom_field(
            "DLS Course",
            {
                "fieldname": "video_link",
                "label": "Video Link",
                "fieldtype": "Data",
                "insert_after": "title",
            }
        )