import frappe

def execute():
    """Add theme fields to Website Settings"""
    doctype = "Website Settings"
    
    # Add theme fields if they don't exist
    fields = [
        {
            "fieldname": "primary_color",
            "label": "Primary Color",
            "fieldtype": "Color",
            "default": "#4338CA",
        },
        {
            "fieldname": "secondary_color",
            "label": "Secondary Color",
            "fieldtype": "Color",
            "default": "#6366F1",
        },
        {
            "fieldname": "background_color",
            "label": "Background Color",
            "fieldtype": "Color",
            "default": "#FFFFFF",
        },
        {
            "fieldname": "text_color",
            "label": "Text Color",
            "fieldtype": "Color",
            "default": "#111827",
        },
    ]
    
    for field in fields:
        if not frappe.db.exists("DocField", {"parent": doctype, "fieldname": field["fieldname"]}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": doctype,
                "fieldname": field["fieldname"],
                "label": field["label"],
                "fieldtype": field["fieldtype"],
                "insert_after": "custom_css",
                "default": field["default"],
            }).insert(ignore_permissions=True) 