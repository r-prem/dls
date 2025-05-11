import frappe

def execute():
    doctype = 'DLS Settings'
    fieldname = 'enable_certificates'
    if not frappe.db.exists('DocField', {'parent': doctype, 'fieldname': fieldname}):
        frappe.get_doc({
            'doctype': 'DocField',
            'parent': doctype,
            'parenttype': 'DocType',
            'parentfield': 'fields',
            'fieldname': fieldname,
            'label': 'Enable Certificates',
            'fieldtype': 'Check',
            'insert_after': 'openai_api_key',
            'reqd': 0,
            'default': 1,
            'description': 'If disabled, certificates will not be available for courses.',
        }).insert(ignore_permissions=True)
        frappe.clear_cache(doctype=doctype) 