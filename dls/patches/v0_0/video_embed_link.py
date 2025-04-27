import frappe


def execute():
	courses = frappe.get_all(
		"DLS Course", {"video_link": ["is", "set"]}, ["name", "video_link"]
	)
	for course in courses:
		if course.video_link:
			link = course.video_link.split("/")[-1]
			frappe.db.set_value("DLS Course", course.name, "video_link", link)
