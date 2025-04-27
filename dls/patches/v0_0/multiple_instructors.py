import frappe


def execute():
	frappe.reload_doc("dls", "doctype", "dls_course")
	frappe.reload_doc("dls", "doctype", "course_instructor")
	courses = frappe.get_all("DLS Course", fields=["name", "instructor"])
	for course in courses:
		doc = frappe.get_doc(
			{
				"doctype": "Course Instructor",
				"parent": course.name,
				"parentfield": "instructors",
				"parenttype": "DLS Course",
				"instructor": course.instructor,
			}
		)
		doc.save()
