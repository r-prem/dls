import frappe

def execute():
    doctype = 'DLS Settings'
    fieldname = 'enable_quizzes'
    if not frappe.db.exists('DocField', {'parent': doctype, 'fieldname': fieldname}):
        frappe.get_doc({
            'doctype': 'DocField',
            'parent': doctype,
            'parenttype': 'DocType',
            'parentfield': 'fields',
            'fieldname': fieldname,
            'label': 'Enable Quizzes',
            'fieldtype': 'Check',
            'insert_after': 'enable_certificates',
            'reqd': 0,
            'default': 1,
            'description': 'If disabled, quizzes will not be available in lessons.',
        }).insert(ignore_permissions=True)
        frappe.clear_cache(doctype=doctype) 