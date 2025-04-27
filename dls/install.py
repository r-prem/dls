import frappe
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to
from dls.dls.api import give_dicussions_permission


def after_install():
	create_batch_source()
	give_dicussions_permission()


def after_sync():
	create_dls_roles()
	set_default_certificate_print_format()
	add_all_roles_to("Administrator")


def before_uninstall():
	delete_custom_fields()
	delete_dls_roles()


def create_dls_roles():
	create_course_creator_role()
	create_moderator_role()
	create_evaluator_role()
	create_dls_student_role()


def delete_dls_roles():
	roles = ["Course Creator", "Moderator"]
	for role in roles:
		if frappe.db.exists("Role", role):
			frappe.db.delete("Role", role)


def create_course_creator_role():
	if frappe.db.exists("Role", "Course Creator"):
		frappe.db.set_value("Role", "Course Creator", "desk_access", 0)
	else:
		role = frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": "Course Creator",
				"home_page": "",
				"desk_access": 0,
			}
		)
		role.save()


def create_moderator_role():
	if frappe.db.exists("Role", "Moderator"):
		frappe.db.set_value("Role", "Moderator", "desk_access", 0)
	else:
		role = frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": "Moderator",
				"home_page": "",
				"desk_access": 0,
			}
		)
		role.save()


def create_evaluator_role():
	if frappe.db.exists("Role", "Batch Evaluator"):
		frappe.db.set_value("Role", "Batch Evaluator", "desk_access", 0)
	else:
		role = frappe.new_doc("Role")
		role.update(
			{
				"role_name": "Batch Evaluator",
				"home_page": "",
				"desk_access": 0,
			}
		)
		role.save()


def create_dls_student_role():
	if frappe.db.exists("Role", "DLS Student"):
		frappe.db.set_value("Role", "DLS Student", "desk_access", 0)
	else:
		role = frappe.new_doc("Role")
		role.update(
			{
				"role_name": "DLS Student",
				"home_page": "",
				"desk_access": 0,
			}
		)
		role.save()


def set_default_certificate_print_format():
	filters = {
		"doc_type": "DLS Certificate",
		"property": "default_print_format",
	}
	if not frappe.db.exists("Property Setter", filters):
		filters.update(
			{
				"doctype_or_field": "DocType",
				"property_type": "Data",
				"value": "Certificate",
			}
		)

		doc = frappe.new_doc("Property Setter")
		doc.update(filters)
		doc.save()


def delete_custom_fields():
	fields = [
		"user_category",
		"headline",
		"college",
		"city",
		"verify_terms",
		"country",
		"preferred_location",
		"preferred_functions",
		"preferred_industries",
		"work_environment_column",
		"time",
		"role",
		"carrer_preference_details",
		"skill",
		"certification_details",
		"internship",
		"branch",
		"github",
		"medium",
		"linkedin",
		"profession",
		"looking_for_job",
		"cover_image" "work_environment",
		"dream_companies",
		"career_preference_column",
		"attire",
		"collaboration",
		"location_preference",
		"company_type",
		"skill_details",
		"certification",
		"education",
		"work_experience",
		"education_details",
		"hide_private",
		"work_experience_details",
		"profile_complete",
	]

	for field in fields:
		frappe.db.delete("Custom Field", {"fieldname": field})


def create_batch_source():
	sources = [
		"Newsletter",
		"LinkedIn",
		"Twitter",
		"Website",
		"Friend/Colleague/Connection",
		"Google Search",
	]

	for source in sources:
		if not frappe.db.exists("DLS Source", source):
			doc = frappe.new_doc("DLS Source")
			doc.source = source
			doc.save()
