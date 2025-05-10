import frappe

def execute():
    doctype = 'DLS Settings'
    fieldname = 'openai_api_key'
    if not frappe.db.exists('DocField', {'parent': doctype, 'fieldname': fieldname}):
        frappe.get_doc({
            'doctype': 'DocField',
            'parent': doctype,
            'parenttype': 'DocType',
            'parentfield': 'fields',
            'fieldname': fieldname,
            'label': 'OpenAI API Key',
            'fieldtype': 'Password',
            'insert_after': 'unsplash_access_key',
            'reqd': 0,
            'description': 'Your OpenAI API key. You can get this from https://platform.openai.com/account/api-keys',
        }).insert(ignore_permissions=True)
        frappe.clear_cache(doctype=doctype) 