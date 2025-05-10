import frappe

def execute():
    # Get the default certificate template from DLS Settings
    default_template = frappe.db.get_single_value('DLS Settings', 'default_certificate_template')
    
    if default_template:
        # Check if property setter exists
        property_setter = frappe.db.exists('Property Setter', {
            'doc_type': 'DLS Certificate',
            'property': 'default_print_format'
        })
        
        if property_setter:
            # Update existing property setter
            frappe.db.set_value('Property Setter', property_setter, 'value', default_template)
        else:
            # Create new property setter
            frappe.make_property_setter({
                'doctype': 'DLS Certificate',
                'property': 'default_print_format',
                'value': default_template,
                'property_type': 'Data'
            }) 