"""API methods for the DLS.
"""

import json
import frappe
import zipfile
import os
import re
import shutil
import requests
import xml.etree.ElementTree as ET
from frappe.translate import get_all_translations
from frappe import _
from frappe.utils import (
	get_datetime,
	cint,
	flt,
	now,
	add_days,
	format_date,
	date_diff,
)
from frappe.query_builder import DocType
from pypika.functions import DistinctOptionFunction
from dls.dls.utils import get_average_rating, get_lesson_count
from xml.dom.minidom import parseString
from dls.dls.doctype.course_lesson.course_lesson import save_progress
from frappe.integrations.frappe_providers.frappecloud_billing import (
	is_fc_site,
	current_site_info,
)


@frappe.whitelist()
def autosave_section(section, code):
	"""Saves the code edited in one of the sections."""
	doc = frappe.get_doc(
		doctype="Code Revision", section=section, code=code, author=frappe.session.user
	)
	doc.insert()
	return {"name": doc.name}


@frappe.whitelist()
def submit_solution(exercise, code):
	"""Submits a solution.

	@exerecise: name of the exercise to submit
	@code: solution to the exercise
	"""
	ex = frappe.get_doc("DLS Exercise", exercise)
	if not ex:
		return
	doc = ex.submit(code)
	return {"name": doc.name, "creation": doc.creation}


@frappe.whitelist()
def save_current_lesson(course_name, lesson_name):
	"""Saves the current lesson for a student/mentor."""
	name = frappe.get_value(
		doctype="DLS Enrollment",
		filters={"course": course_name, "member": frappe.session.user},
		fieldname="name",
	)
	if not name:
		return
	frappe.db.set_value("DLS Enrollment", name, "current_lesson", lesson_name)


@frappe.whitelist()
def join_cohort(course, cohort, subgroup, invite_code):
	"""Creates a Cohort Join Request for given user."""
	course_doc = frappe.get_doc("DLS Course", course)
	cohort_doc = course_doc and course_doc.get_cohort(cohort)
	subgroup_doc = cohort_doc and cohort_doc.get_subgroup(subgroup)

	if not subgroup_doc or subgroup_doc.invite_code != invite_code:
		return {"ok": False, "error": "Invalid join link"}

	data = {
		"doctype": "Cohort Join Request",
		"cohort": cohort_doc.name,
		"subgroup": subgroup_doc.name,
		"email": frappe.session.user,
		"status": "Pending",
	}
	# Don't insert duplicate records
	if frappe.db.exists(data):
		return {"ok": True, "status": "record found"}
	else:
		doc = frappe.get_doc(data)
		doc.insert()
		return {"ok": True, "status": "record created"}


@frappe.whitelist()
def approve_cohort_join_request(join_request):
	r = frappe.get_doc("Cohort Join Request", join_request)
	sg = r and frappe.get_doc("Cohort Subgroup", r.subgroup)
	if not sg or r.status not in ["Pending", "Accepted"]:
		return {"ok": False, "error": "Invalid Join Request"}
	if (
		not sg.is_manager(frappe.session.user) and "System Manager" not in frappe.get_roles()
	):
		return {"ok": False, "error": "Permission Deined"}

	r.status = "Accepted"
	r.save()
	return {"ok": True}


@frappe.whitelist()
def reject_cohort_join_request(join_request):
	r = frappe.get_doc("Cohort Join Request", join_request)
	sg = r and frappe.get_doc("Cohort Subgroup", r.subgroup)
	if not sg or r.status not in ["Pending", "Rejected"]:
		return {"ok": False, "error": "Invalid Join Request"}
	if (
		not sg.is_manager(frappe.session.user) and "System Manager" not in frappe.get_roles()
	):
		return {"ok": False, "error": "Permission Deined"}

	r.status = "Rejected"
	r.save()
	return {"ok": True}


@frappe.whitelist()
def undo_reject_cohort_join_request(join_request):
	r = frappe.get_doc("Cohort Join Request", join_request)
	sg = r and frappe.get_doc("Cohort Subgroup", r.subgroup)
	# keeping Pending as well to consider the case of duplicate requests
	if not sg or r.status not in ["Pending", "Rejected"]:
		return {"ok": False, "error": "Invalid Join Request"}
	if (
		not sg.is_manager(frappe.session.user) and "System Manager" not in frappe.get_roles()
	):
		return {"ok": False, "error": "Permission Deined"}

	r.status = "Pending"
	r.save()
	return {"ok": True}


@frappe.whitelist()
def add_mentor_to_subgroup(subgroup, email):
	try:
		sg = frappe.get_doc("Cohort Subgroup", subgroup)
	except frappe.DoesNotExistError:
		return {"ok": False, "error": f"Invalid subgroup: {subgroup}"}

	if (
		not sg.get_cohort().is_admin(frappe.session.user)
		and "System Manager" not in frappe.get_roles()
	):
		return {"ok": False, "error": "Permission Deined"}

	try:
		user = frappe.get_doc("User", email)
	except frappe.DoesNotExistError:
		return {"ok": False, "error": f"Invalid user: {email}"}

	sg.add_mentor(email)
	return {"ok": True}


@frappe.whitelist(allow_guest=True)
def get_user_info():
	if frappe.session.user == "Guest":
		return None

	user = frappe.db.get_value(
		"User",
		frappe.session.user,
		["name", "email", "enabled", "user_image", "full_name", "user_type", "username"],
		as_dict=1,
	)
	user["roles"] = frappe.get_roles(user.name)
	user.is_instructor = "Course Creator" in user.roles
	user.is_moderator = "Moderator" in user.roles
	user.is_evaluator = "Batch Evaluator" in user.roles
	user.is_student = (
		not user.is_instructor and not user.is_moderator and not user.is_evaluator
	)
	user.is_fc_site = is_fc_site()
	user.is_system_manager = "System Manager" in user.roles
	user.sitename = frappe.local.site
	user.developer_mode = frappe.conf.developer_mode
	if user.is_fc_site and user.is_system_manager:
		user.site_info = current_site_info()
	return user


@frappe.whitelist(allow_guest=True)
def get_system_language():
	"""Get the system's default language."""
	try:
		# First try to get user's language if logged in
		#if frappe.session.user != "Guest":
		#	lang = frappe.db.get_value("User", frappe.session.user, "language")
		#	if lang:
		#		return {"language": lang}
		
		# Fallback to system settings
		lang = frappe.db.get_single_value("System Settings", "language")
		return {"language": lang or "en"}
	except Exception:
		return {"language": "en"}


@frappe.whitelist(allow_guest=True)
def get_translations(lang=None):
	"""Get translations for the specified language or user's preferred language.
	
	Args:
		lang (str, optional): Language code (e.g. 'de' for German). Defaults to None.
	"""
	if not lang:
		if frappe.session.user != "Guest":
			lang = frappe.db.get_value("User", frappe.session.user, "language")
		else:
			lang = frappe.db.get_single_value("System Settings", "language")
	
	# Set the language in the session for consistency
	frappe.local.lang = lang
	return get_all_translations(lang)


@frappe.whitelist()
def validate_billing_access(billing_type, name):
	access = True
	message = ""
	doctype = "DLS Batch" if billing_type == "batch" else "DLS Course"

	if frappe.session.user == "Guest":
		access = False
		message = _("Please login to continue with payment.")

	if access and billing_type not in ["course", "batch", "certificate"]:
		access = False
		message = _("Module is incorrect.")

	if access and not frappe.db.exists(doctype, name):
		access = False
		message = _("Module Name is incorrect or does not exist.")

	if access and billing_type == "course":
		membership = frappe.db.exists(
			"DLS Enrollment", {"member": frappe.session.user, "course": name}
		)
		if membership:
			access = False
			message = _("You are already enrolled for this course.")

	elif access and billing_type == "batch":
		membership = frappe.db.exists(
			"DLS Batch Enrollment", {"member": frappe.session.user, "batch": name}
		)
		if membership:
			access = False
			message = _("You are already enrolled for this batch.")

		seat_count = frappe.get_cached_value("DLS Batch", name, "seat_count")
		number_of_students = frappe.db.count("DLS Batch Enrollment", {"batch": name})
		if seat_count <= number_of_students:
			access = False
			message = _("Batch is sold out.")

	elif access and billing_type == "certificate":
		purchased_certificate = frappe.db.exists(
			"DLS Enrollment",
			{
				"course": name,
				"member": frappe.session.user,
				"purchased_certificate": 1,
			},
		)
		if purchased_certificate:
			access = False
			message = _("You have already purchased the certificate for this course.")

	address = frappe.db.get_value(
		"Address",
		{"email_id": frappe.session.user},
		[
			"name",
			"address_title as billing_name",
			"address_line1",
			"address_line2",
			"city",
			"state",
			"country",
			"pincode",
			"phone",
		],
		as_dict=1,
	)

	return {"access": access, "message": message, "address": address}


@frappe.whitelist(allow_guest=True)
def get_job_details(job):
	return frappe.db.get_value(
		"Job Opportunity",
		job,
		[
			"job_title",
			"location",
			"type",
			"company_name",
			"company_logo",
			"company_website",
			"name",
			"creation",
			"description",
			"owner",
		],
		as_dict=1,
	)


@frappe.whitelist(allow_guest=True)
def get_job_opportunities(filters=None, orFilters=None):
	if not filters:
		filters = {}

	jobs = frappe.get_all(
		"Job Opportunity",
		filters=filters,
		or_filters=orFilters,
		fields=[
			"job_title",
			"location",
			"type",
			"company_name",
			"company_logo",
			"name",
			"creation",
		],
		order_by="creation desc",
	)
	return jobs


@frappe.whitelist(allow_guest=True)
def get_chart_details():
	details = frappe._dict()
	details.enrollments = frappe.db.count("DLS Enrollment")
	details.courses = frappe.db.count(
		"DLS Course",
		{
			"published": 1,
			"upcoming": 0,
		},
	)
	details.users = frappe.db.count(
		"User", {"enabled": 1, "name": ["not in", ("Administrator", "Guest")]}
	)
	details.completions = frappe.db.count(
		"DLS Enrollment", {"progress": ["like", "%100%"]}
	)
	details.lesson_completions = frappe.db.count("DLS Course Progress")
	return details


@frappe.whitelist()
def get_file_info(file_url):
	"""Get file info for the given file URL."""
	file_info = frappe.db.get_value(
		"File", {"file_url": file_url}, ["file_name", "file_size", "file_url"], as_dict=1
	)
	return file_info


@frappe.whitelist(allow_guest=True)
def get_branding():
	"""Get branding details."""
	website_settings = frappe.get_single("Website Settings")
	image_fields = ["banner_image", "footer_logo", "favicon"]

	for field in image_fields:
		if website_settings.get(field):
			file_info = get_file_info(website_settings.get(field))
			website_settings.update({field: json.loads(json.dumps(file_info))})
		else:
			website_settings.update({field: None})

	return website_settings


@frappe.whitelist()
def get_unsplash_photos(keyword=None):
	from dls.unsplash import get_list, get_by_keyword

	if keyword:
		return get_by_keyword(keyword)

	return frappe.cache().get_value("unsplash_photos", generator=get_list)


@frappe.whitelist()
def get_evaluator_details(evaluator):
	frappe.only_for("Batch Evaluator")

	if not frappe.db.exists("Google Calendar", {"user": evaluator}):
		calendar = frappe.new_doc("Google Calendar")
		calendar.update({"user": evaluator, "calendar_name": evaluator})
		calendar.insert()
	else:
		calendar = frappe.db.get_value(
			"Google Calendar", {"user": evaluator}, ["name", "authorization_code"], as_dict=1
		)

	if frappe.db.exists("Course Evaluator", {"evaluator": evaluator}):
		doc = frappe.get_doc("Course Evaluator", evaluator)
	else:
		doc = frappe.new_doc("Course Evaluator")
		doc.evaluator = evaluator
		doc.insert()

	return {
		"slots": doc.as_dict(),
		"calendar": calendar.name,
		"is_authorised": calendar.authorization_code,
	}


@frappe.whitelist(allow_guest=True)
def get_certified_participants(filters=None, start=0, page_length=30):
	or_filters = {}
	if not filters:
		filters = {}

	filters.update({"published": 1})

	category = filters.get("category")
	if category:
		del filters["category"]
		or_filters["course_title"] = ["like", f"%{category}%"]
		or_filters["batch_title"] = ["like", f"%{category}%"]

	participants = frappe.db.get_all(
		"DLS Certificate",
		filters=filters,
		or_filters=or_filters,
		fields=["member", "issue_date"],
		group_by="member",
		order_by="issue_date desc",
		start=start,
		page_length=page_length,
	)

	for participant in participants:
		count = frappe.db.count("DLS Certificate", {"member": participant.member})
		details = frappe.db.get_value(
			"User",
			participant.member,
			["full_name", "user_image", "username", "country", "headline"],
			as_dict=1,
		)
		details["certificate_count"] = count
		participant.update(details)

	return participants


class CountDistinct(DistinctOptionFunction):
	def __init__(self, field):
		super().__init__("COUNT", field, distinct=True)


@frappe.whitelist(allow_guest=True)
def get_count_of_certified_members():
	Certificate = DocType("DLS Certificate")

	query = (
		frappe.qb.from_(Certificate)
		.select(CountDistinct(Certificate.member).as_("total"))
		.where(Certificate.published == 1)
	)

	result = query.run(as_dict=True)
	return result[0]["total"] if result else 0


@frappe.whitelist(allow_guest=True)
def get_certification_categories():
	categories = []
	docs = frappe.get_all(
		"DLS Certificate",
		filters={
			"published": 1,
		},
		fields=["course_title", "batch_title"],
	)

	for doc in docs:
		category = doc.course_title if doc.course_title else doc.batch_title
		if category not in categories:
			categories.append(category)

	return categories


@frappe.whitelist()
def get_assigned_badges(member):
	assigned_badges = frappe.get_all(
		"DLS Badge Assignment",
		{"member": member},
		["badge"],
		as_dict=1,
	)

	for badge in assigned_badges:
		badge.update(
			frappe.db.get_value("DLS Badge", badge.badge, ["name", "title", "image"])
		)
	return assigned_badges


@frappe.whitelist()
def get_all_users():
	frappe.only_for(["Moderator", "Course Creator", "Batch Evaluator"])
	users = frappe.get_all(
		"User",
		{
			"enabled": 1,
		},
		["name", "full_name", "user_image"],
	)

	return {user.name: user for user in users}


@frappe.whitelist()
def mark_as_read(name):
	doc = frappe.get_doc("Notification Log", name)
	doc.read = 1
	doc.save(ignore_permissions=True)


@frappe.whitelist()
def mark_all_as_read():
	notifications = frappe.get_all(
		"Notification Log", {"for_user": frappe.session.user, "read": 0}, pluck="name"
	)

	for notification in notifications:
		mark_as_read(notification)


@frappe.whitelist(allow_guest=True)
def get_sidebar_settings():
	dls_settings = frappe.get_single("DLS Settings")
	sidebar_items = frappe._dict()

	items = [
		"courses",
		"batches",
		"certified_participants",
		"jobs",
		"statistics",
		"notifications",
		"assignments",
		"programs",
	]
	for item in items:
		sidebar_items[item] = dls_settings.get(item)

	if len(dls_settings.sidebar_items):
		web_pages = frappe.get_all(
			"DLS Sidebar Item",
			{"parenttype": "DLS Settings", "parentfield": "sidebar_items"},
			["web_page", "route", "title as label", "icon"],
		)
		for page in web_pages:
			page.to = page.route

		sidebar_items.web_pages = web_pages

	return sidebar_items


@frappe.whitelist()
def update_sidebar_item(webpage, icon):
	filters = {
		"web_page": webpage,
		"parenttype": "DLS Settings",
		"parentfield": "sidebar_items",
		"parent": "DLS Settings",
	}

	if frappe.db.exists("DLS Sidebar Item", filters):
		frappe.db.set_value("DLS Sidebar Item", filters, "icon", icon)
	else:
		doc = frappe.new_doc("DLS Sidebar Item")
		doc.update(filters)
		doc.icon = icon
		doc.insert()


@frappe.whitelist()
def delete_sidebar_item(webpage):
	return frappe.db.delete(
		"DLS Sidebar Item",
		{
			"web_page": webpage,
			"parenttype": "DLS Settings",
			"parentfield": "sidebar_items",
			"parent": "DLS Settings",
		},
	)


@frappe.whitelist()
def delete_lesson(lesson, chapter):
	# Delete Reference
	chapter = frappe.get_doc("Course Chapter", chapter)
	chapter.lessons = [row for row in chapter.lessons if row.lesson != lesson]
	chapter.save()

	# Delete progress
	frappe.db.delete("DLS Course Progress", {"lesson": lesson})

	# Delete Lesson
	frappe.db.delete("Course Lesson", lesson)


@frappe.whitelist()
def update_lesson_index(lesson, sourceChapter, targetChapter, idx):
	hasMoved = sourceChapter == targetChapter

	update_source_chapter(lesson, sourceChapter, idx, hasMoved)
	if not hasMoved:
		update_target_chapter(lesson, targetChapter, idx)


def update_source_chapter(lesson, chapter, idx, hasMoved=False):
	lessons = frappe.get_all(
		"Lesson Reference",
		{
			"parent": chapter,
		},
		pluck="lesson",
		order_by="idx",
	)

	lessons.remove(lesson)
	if not hasMoved:
		frappe.db.delete("Lesson Reference", {"parent": chapter, "lesson": lesson})
	else:
		lessons.insert(idx, lesson)

	update_index(lessons, chapter)


def update_target_chapter(lesson, chapter, idx):
	lessons = frappe.get_all(
		"Lesson Reference",
		{
			"parent": chapter,
		},
		pluck="lesson",
		order_by="idx",
	)

	lessons.insert(idx, lesson)
	new_lesson_reference = frappe.new_doc("Lesson Reference")
	new_lesson_reference.update(
		{
			"lesson": lesson,
			"parent": chapter,
			"parenttype": "Course Chapter",
			"parentfield": "lessons",
		}
	)
	new_lesson_reference.insert()
	update_index(lessons, chapter)


def update_index(lessons, chapter):
	for row in lessons:
		frappe.db.set_value(
			"Lesson Reference", {"lesson": row, "parent": chapter}, "idx", lessons.index(row) + 1
		)


@frappe.whitelist(allow_guest=True)
def get_categories(doctype, filters):
	categoryOptions = []

	categories = frappe.get_all(
		doctype,
		filters,
		pluck="category",
	)
	categories = list(set(categories))

	for category in categories:
		if category:
			categoryOptions.append({"label": category, "value": category})

	return categoryOptions


@frappe.whitelist()
def get_members(start=0, search=""):
	"""Get members for the given search term and start index.
	                                Args: start (int): Start index for the query.
	<<<<<<< HEAD
	                                search (str): Search term to filter the results.
	=======
	                                                                                                                                                                search (str): Search term to filter the results.
	>>>>>>> 4869bba7bbb2fb38477d6fc29fb3b5838e075577
	                                Returns: List of members.
	"""

	filters = {"enabled": 1, "name": ["not in", ["Administrator", "Guest"]]}
	or_filters = {}

	if search:
		or_filters["full_name"] = ["like", f"%{search}%"]
		or_filters["email"] = ["like", f"%{search}%"]

	members = frappe.get_all(
		"User",
		filters=filters,
		fields=["name", "full_name", "user_image", "username", "last_active"],
		or_filters=or_filters,
		page_length=20,
		start=start,
	)

	for member in members:
		roles = frappe.get_roles(member.name)
		if "Moderator" in roles:
			member.role = "Moderator"
		elif "Course Creator" in roles:
			member.role = "Course Creator"
		elif "Batch Evaluator" in roles:
			member.role = "Batch Evaluator"
		elif "DLS Student" in roles:
			member.role = "DLS Student"

	return members


def check_app_permission():
	"""Check if the user has permission to access the app."""
	if frappe.session.user == "Administrator":
		return True

	roles = frappe.get_roles()
	dls_roles = ["Moderator", "Course Creator", "Batch Evaluator", "DLS Student"]
	if any(role in roles for role in dls_roles):
		return True

	return False


@frappe.whitelist()
def save_evaluation_details(
	member,
	course,
	batch_name,
	evaluator,
	date,
	start_time,
	end_time,
	status,
	rating,
	summary,
):
	"""
	Save evaluation details for a member against a course.
	"""
	evaluation = frappe.db.exists(
		"DLS Certificate Evaluation", {"member": member, "course": course}
	)

	details = {
		"date": date,
		"start_time": start_time,
		"end_time": end_time,
		"status": status,
		"rating": rating / 5,
		"summary": summary,
		"batch_name": batch_name,
	}

	if evaluation:
		frappe.db.set_value("DLS Certificate Evaluation", evaluation, details)
		return evaluation
	else:
		doc = frappe.new_doc("DLS Certificate Evaluation")
		details.update(
			{
				"member": member,
				"course": course,
				"evaluator": evaluator,
			}
		)
		doc.update(details)
		doc.insert()
		return doc.name


@frappe.whitelist()
def save_certificate_details(
	member,
	course,
	batch_name,
	evaluator,
	issue_date,
	expiry_date,
	template,
	published=True,
):
	"""
	Save certificate details for a member against a course.
	"""
	certificate = frappe.db.exists("DLS Certificate", {"member": member, "course": course})

	details = {
		"published": published,
		"issue_date": issue_date,
		"expiry_date": expiry_date,
		"template": template,
		"batch_name": batch_name,
	}

	if certificate:
		frappe.db.set_value("DLS Certificate", certificate, details)
		return certificate
	else:
		doc = frappe.new_doc("DLS Certificate")
		details.update(
			{
				"member": member,
				"course": course,
				"evaluator": evaluator,
			}
		)
		doc.update(details)
		doc.insert()
		return doc.name


@frappe.whitelist()
def delete_documents(doctype, documents):
	frappe.only_for("Moderator")
	for doc in documents:
		frappe.delete_doc(doctype, doc)


@frappe.whitelist()
def get_payment_gateway_details(payment_gateway):
	fields = []
	gateway = frappe.get_doc("Payment Gateway", payment_gateway)

	if gateway.gateway_controller is None:
		try:
			data = frappe.get_doc(f"{payment_gateway} Settings").as_dict()
			meta = frappe.get_meta(f"{payment_gateway} Settings").fields
			doctype = f"{payment_gateway} Settings"
			docname = f"{payment_gateway} Settings"
		except Exception:
			frappe.throw(_("{0} Settings not found").format(payment_gateway))
	else:
		try:
			data = frappe.get_doc(gateway.gateway_settings, gateway.gateway_controller).as_dict()
			meta = frappe.get_meta(gateway.gateway_settings).fields
			doctype = gateway.gateway_settings
			docname = gateway.gateway_controller
		except Exception:
			frappe.throw(_("{0} Settings not found").format(payment_gateway))

	for row in meta:
		if row.fieldtype not in ["Column Break", "Section Break"]:
			if row.fieldtype in ["Attach", "Attach Image"]:
				fieldtype = "Upload"
				data[row.fieldname] = get_file_info(data.get(row.fieldname))
			else:
				fieldtype = row.fieldtype

			fields.append(
				{
					"label": row.label,
					"name": row.fieldname,
					"type": fieldtype,
				}
			)

	return {
		"fields": fields,
		"data": data,
		"doctype": doctype,
		"docname": docname,
	}


def update_course_statistics():
	courses = frappe.get_all("DLS Course", fields=["name"])

	for course in courses:
		lessons = get_lesson_count(course.name)

		enrollments = frappe.db.count(
			"DLS Enrollment", {"course": course.name, "member_type": "Student"}
		)

		avg_rating = get_average_rating(course.name) or 0
		avg_rating = flt(avg_rating, frappe.get_system_settings("float_precision") or 3)

		frappe.db.set_value(
			"DLS Course",
			course.name,
			{"lessons": lessons, "enrollments": enrollments, "rating": avg_rating},
		)


@frappe.whitelist()
def get_announcements(batch):
	communications = frappe.get_all(
		"Communication",
		filters={
			"reference_doctype": "DLS Batch",
			"reference_name": batch,
		},
		fields=[
			"subject",
			"content",
			"recipients",
			"cc",
			"communication_date",
			"sender",
			"sender_full_name",
		],
		order_by="communication_date desc",
	)

	for communication in communications:
		communication.image = frappe.get_cached_value(
			"User", communication.sender, "user_image"
		)

	return communications


@frappe.whitelist()
def delete_course(course):

	chapters = frappe.get_all("Course Chapter", {"course": course}, pluck="name")

	chapter_references = frappe.get_all(
		"Chapter Reference", {"parent": course}, pluck="name"
	)

	for chapter in chapters:
		lessons = frappe.get_all("Course Lesson", {"chapter": chapter}, pluck="name")

		lesson_references = frappe.get_all(
			"Lesson Reference", {"parent": chapter}, pluck="name"
		)

		for lesson in lesson_references:
			frappe.delete_doc("Lesson Reference", lesson)

		for lesson in lessons:
			topics = frappe.get_all(
				"Discussion Topic",
				{"reference_doctype": "Course Lesson", "reference_docname": lesson},
				pluck="name",
			)

			for topic in topics:
				frappe.db.delete("Discussion Reply", {"topic": topic})

				frappe.db.delete("Discussion Topic", topic)

			frappe.delete_doc("Course Lesson", lesson)

	for chapter in chapter_references:
		frappe.delete_doc("Chapter Reference", chapter)

	for chapter in chapters:
		frappe.delete_doc("Course Chapter", chapter)

	frappe.db.delete("DLS Course Progress", {"course": course})
	frappe.db.delete("DLS Quiz", {"course": course})
	frappe.db.delete("DLS Quiz Submission", {"course": course})
	frappe.db.delete("DLS Enrollment", {"course": course})
	frappe.delete_doc("DLS Course", course)


def give_dicussions_permission():
	doctypes = ["Discussion Topic", "Discussion Reply"]
	roles = ["DLS Student", "Course Creator", "Moderator", "Batch Evaluator"]
	for doctype in doctypes:
		for role in roles:
			if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role}):
				frappe.get_doc(
					{
						"doctype": "Custom DocPerm",
						"parent": doctype,
						"role": role,
						"read": 1,
						"write": 1,
						"create": 1,
						"delete": 1,
					}
				).save(ignore_permissions=True)


@frappe.whitelist()
def upsert_chapter(title, course, is_scorm_package, scorm_package, name=None):
	values = frappe._dict(
		{"title": title, "course": course, "is_scorm_package": is_scorm_package}
	)

	if is_scorm_package:
		scorm_package = frappe._dict(scorm_package)
		extract_path = extract_package(course, title, scorm_package)

		values.update(
			{
				"scorm_package": scorm_package.name,
				"scorm_package_path": extract_path.split("public")[1],
				"manifest_file": get_manifest_file(extract_path).split("public")[1],
				"launch_file": get_launch_file(extract_path).split("public")[1],
			}
		)

	if name:
		chapter = frappe.get_doc("Course Chapter", name)
	else:
		chapter = frappe.new_doc("Course Chapter")

	chapter.update(values)
	chapter.save()

	if is_scorm_package and not len(chapter.lessons):
		add_lesson(title, chapter.name, course)

	return chapter


def extract_package(course, title, scorm_package):
	package = frappe.get_doc("File", scorm_package.name)
	zip_path = package.get_full_path()
	# check_for_malicious_code(zip_path)
	extract_path = frappe.get_site_path("public", "scorm", course, title)
	zipfile.ZipFile(zip_path).extractall(extract_path)
	return extract_path


def check_for_malicious_code(zip_path):
	suspicious_patterns = [
		# Unsafe inline JavaScript
		r'on(click|load|mouseover|error|submit|focus|blur|change|keyup|keydown|keypress|resize)=".*?"',  # Inline event handlers (e.g., onerror, onclick)
		r'<script.*?src=["\']http',  # External script tags
		r"eval\(",  # Usage of eval()
		r"Function\(",  # Usage of Function constructor
		r"(btoa|atob)\(",  # Base64 encoding/decoding
		# Dangerous XML patterns
		r"<!ENTITY",  # XXE-related
		r"<\?xml-stylesheet .*?>",  # External stylesheets in XML
	]

	with zipfile.ZipFile(zip_path, "r") as zf:
		for file_name in zf.namelist():
			if file_name.endswith((".html", ".js", ".xml")):
				with zf.open(file_name) as file:
					content = file.read().decode("utf-8", errors="ignore")
					for pattern in suspicious_patterns:
						if re.search(pattern, content):
							frappe.throw(
								_("Suspicious pattern found in {0}: {1}").format(file_name, pattern)
							)


def get_manifest_file(extract_path):
	manifest_file = None
	for root, dirs, files in os.walk(extract_path):
		for file in files:
			if file == "imsmanifest.xml":
				manifest_file = os.path.join(root, file)
				break
		if manifest_file:
			break
	return manifest_file


def get_launch_file(extract_path):
	launch_file = None
	manifest_file = get_manifest_file(extract_path)

	if manifest_file:
		with open(manifest_file) as file:
			data = file.read()
			dom = parseString(data)
			resource = dom.getElementsByTagName("resource")
			for res in resource:
				if (
					res.getAttribute("adlcp:scormtype") == "sco"
					or res.getAttribute("adlcp:scormType") == "sco"
				):
					launch_file = res.getAttribute("href")
					break

		if launch_file:
			launch_file = os.path.join(os.path.dirname(manifest_file), launch_file)

	return launch_file


def add_lesson(title, chapter, course):
	lesson = frappe.new_doc("Course Lesson")
	lesson.update(
		{
			"title": title,
			"chapter": chapter,
			"course": course,
		}
	)
	lesson.insert()

	lesson_reference = frappe.new_doc("Lesson Reference")
	lesson_reference.update(
		{
			"lesson": lesson.name,
			"parent": chapter,
			"parenttype": "Course Chapter",
			"parentfield": "lessons",
		}
	)
	lesson_reference.insert()


@frappe.whitelist()
def delete_chapter(chapter):
	chapterInfo = frappe.db.get_value(
		"Course Chapter", chapter, ["is_scorm_package", "scorm_package_path"], as_dict=True
	)

	if chapterInfo.is_scorm_package:
		delete_scorm_package(chapterInfo.scorm_package_path)

	frappe.db.delete("Chapter Reference", {"chapter": chapter})
	frappe.db.delete("Lesson Reference", {"parent": chapter})
	frappe.db.delete("Course Lesson", {"chapter": chapter})
	frappe.db.delete("Course Chapter", chapter)


def delete_scorm_package(scorm_package_path):
	scorm_package_path = frappe.get_site_path("public", scorm_package_path[1:])
	if os.path.exists(scorm_package_path):
		shutil.rmtree(scorm_package_path)


@frappe.whitelist()
def mark_lesson_progress(course, chapter_number, lesson_number):
	chapter_name = frappe.get_value(
		"Chapter Reference", {"parent": course, "idx": chapter_number}, "chapter"
	)
	lesson_name = frappe.get_value(
		"Lesson Reference", {"parent": chapter_name, "idx": lesson_number}, "lesson"
	)
	save_progress(lesson_name, course)


@frappe.whitelist()
def get_heatmap_data(member=None, base_days=200):
	if not member:
		member = frappe.session.user

	base_date, start_date, number_of_days, days = calculate_date_ranges(base_days)
	date_count = initialize_date_count(days)

	lesson_completions, quiz_submissions, assignment_submissions = fetch_activity_data(
		member, start_date
	)
	count_dates(lesson_completions, date_count)
	count_dates(quiz_submissions, date_count)
	count_dates(assignment_submissions, date_count)

	heatmap_data, labels, total_activities, weeks = prepare_heatmap_data(
		start_date, number_of_days, date_count
	)

	return {
		"heatmap_data": heatmap_data,
		"labels": labels,
		"total_activities": total_activities,
		"weeks": weeks,
	}


def calculate_date_ranges(base_days):
	today = format_date(now(), "YYYY-MM-dd")
	day_today = get_datetime(today).strftime("%w")
	padding_end = 6 - cint(day_today)

	base_date = add_days(today, -base_days)
	day_of_base_date = cint(get_datetime(base_date).strftime("%w"))
	start_date = add_days(base_date, -day_of_base_date)
	number_of_days = base_days + day_of_base_date + padding_end
	days = [add_days(start_date, i) for i in range(number_of_days + 1)]

	return base_date, start_date, number_of_days, days


def initialize_date_count(days):
	return {format_date(day, "YYYY-MM-dd"): 0 for day in days}


def fetch_activity_data(member, start_date):
	lesson_completions = frappe.get_all(
		"DLS Course Progress",
		fields=["creation"],
		filters={"member": member, "creation": [">=", start_date]},
	)

	quiz_submissions = frappe.get_all(
		"DLS Quiz Submission",
		fields=["creation"],
		filters={"member": member, "creation": [">=", start_date]},
	)

	assignment_submissions = frappe.get_all(
		"DLS Assignment Submission",
		fields=["creation"],
		filters={"member": member, "creation": [">=", start_date]},
	)

	return lesson_completions, quiz_submissions, assignment_submissions


def count_dates(data, date_count):
	for entry in data:
		date = format_date(entry.creation, "YYYY-MM-dd")
		if date in date_count:
			date_count[date] += 1


def prepare_heatmap_data(start_date, number_of_days, date_count):
	days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
	heatmap_data = {day: [] for day in days_of_week}
	week_count = -(number_of_days // -7)
	labels = [None] * week_count
	last_seen_month = None
	sorted_dates = sorted(date_count.keys())

	for date in sorted_dates:
		activity_count = date_count[date]
		day_of_week = get_datetime(date).strftime("%a")
		current_month = get_datetime(date).strftime("%b")
		column_index = get_week_difference(start_date, date)

		if 0 <= column_index < week_count:
			heatmap_data[day_of_week].append(
				{
					"date": date,
					"count": activity_count,
					"label": f"{activity_count} activities on {format_date(date, 'dd MMM')}",
				}
			)

			if last_seen_month != current_month:
				labels[column_index] = current_month
				last_seen_month = current_month

	for (index, label) in enumerate(labels):
		if not label:
			labels[index] = ""

	formatted_heatmap_data = [
		{"name": day, "data": heatmap_data[day]} for day in days_of_week
	]

	total_activities = sum(date_count.values())
	return formatted_heatmap_data, labels, total_activities, week_count


def get_week_difference(start_date, current_date):
	diff_in_days = date_diff(current_date, start_date)
	return diff_in_days // 7


@frappe.whitelist()
def get_notifications(filters):
	notifications = frappe.get_all(
		"Notification Log",
		filters,
		["subject", "from_user", "link", "read", "name"],
		order_by="creation desc",
	)

	for notification in notifications:
		from_user_details = frappe.db.get_value(
			"User", notification.from_user, ["full_name", "user_image"], as_dict=1
		)
		notification.update(from_user_details)

	return notifications


@frappe.whitelist(allow_guest=True)
def is_guest_allowed():
	return frappe.get_cached_value("DLS Settings", None, "allow_guest_access")


@frappe.whitelist(allow_guest=True)
def is_learning_path_enabled():
	return frappe.get_cached_value("DLS Settings", None, "enable_learning_paths")


@frappe.whitelist()
def cancel_evaluation(evaluation):
	evaluation = frappe._dict(evaluation)

	if evaluation.member != frappe.session.user:
		return

	frappe.db.set_value("DLS Certificate Request", evaluation.name, "status", "Cancelled")
	events = frappe.get_all(
		"Event Participants",
		{
			"email": evaluation.member,
		},
		["parent", "name"],
	)

	for event in events:
		info = frappe.db.get_value("Event", event.parent, ["starts_on", "subject"], as_dict=1)
		date = str(info.starts_on).split(" ")[0]

		if (
			date == str(evaluation.date.format("YYYY-MM-DD"))
			and evaluation.member_name in info.subject
		):
			communication = frappe.db.get_value(
				"Communication",
				{"reference_doctype": "Event", "reference_name": event.parent},
				"name",
			)
			if communication:
				frappe.delete_doc("Communication", communication, ignore_permissions=True)

			frappe.delete_doc("Event Participants", event.name, ignore_permissions=True)
			frappe.delete_doc("Event", event.parent, ignore_permissions=True)


@frappe.whitelist()
def get_certification_details(course):
	membership = None
	filters = {"course": course, "member": frappe.session.user}

	if frappe.db.exists("DLS Enrollment", filters):
		membership = frappe.db.get_value(
			"DLS Enrollment",
			filters,
			["name", "purchased_certificate"],
			as_dict=1,
		)

	paid_certificate = frappe.db.get_value("DLS Course", course, "paid_certificate")
	certificate = frappe.db.get_value(
		"DLS Certificate",
		{"member": frappe.session.user, "course": course},
		["name", "template"],
		as_dict=1,
	)

	return {
		"membership": membership,
		"paid_certificate": paid_certificate,
		"certificate": certificate,
	}


@frappe.whitelist()
def save_role(user, role, value):
	frappe.only_for("Moderator")
	if cint(value):
		doc = frappe.get_doc(
			{
				"doctype": "Has Role",
				"parent": user,
				"role": role,
				"parenttype": "User",
				"parentfield": "roles",
			}
		)
		doc.save(ignore_permissions=True)
	else:
		frappe.db.delete("Has Role", {"parent": user, "role": role})
	return True


@frappe.whitelist()
def add_an_evaluator(email):
	if not frappe.db.exists("User", email):
		user = frappe.new_doc("User")
		user.update(
			{
				"email": email,
				"first_name": email.split("@")[0].capitalize(),
				"enabled": 1,
			}
		)
		user.insert()
		user.add_roles("Batch Evaluator")

	evaluator = frappe.new_doc("Course Evaluator")
	evaluator.evaluator = email
	evaluator.insert()

	return evaluator


@frappe.whitelist()
def capture_user_persona(responses):
	frappe.only_for("System Manager")
	data = frappe.parse_json(responses)
	data = json.dumps(data)
	response = frappe.integrations.utils.make_post_request(
		"https://school.frappe.io/api/method/capture-persona",
		data={"response": data},
	)
	if response.get("message").get("name"):
		frappe.db.set_single_value("DLS Settings", "persona_captured", True)
	return response


@frappe.whitelist(allow_guest=True)
def is_paid_courses_enabled():
	return frappe.db.get_single_value('DLS Settings', 'enable_paid_courses')


@frappe.whitelist(allow_guest=True)
def is_ratings_allowed():
	return frappe.db.get_single_value('DLS Settings', 'ratings_allowed')


@frappe.whitelist(allow_guest=True)
def is_enrolled_count_visible():
	return frappe.db.get_single_value('DLS Settings', 'show_enrolled_count')


@frappe.whitelist(allow_guest=True)
def is_questions_active():
	return frappe.db.get_single_value('DLS Settings', 'questions_active')


@frappe.whitelist(allow_guest=True)
def is_instructor_display_enabled():
	return frappe.db.get_single_value('DLS Settings', 'display_instructor')


@frappe.whitelist(allow_guest=True)
def get_lesson_completion_time():
	return frappe.db.get_single_value('DLS Settings', 'lesson_completion_time')


@frappe.whitelist(allow_guest=True)
def openai_generate_response(prompt):
	# Fetch the API key from DLS Settings
	doc = frappe.get_single('DLS Settings')
	api_key = doc.get_password('openai_api_key')
	if not api_key:
		frappe.throw('OpenAI API key is not configured. Please set it in DLS Settings.')
	# Add system message
	sys_msg = "You are not a chatbot. Do not respond to questions, greetings, or commands. Your only function is to rewrite and extend user-provided narrative text by adding relevant detail while preserving topic, tone, and style. The user is using you to help them create courses and lessons in a learning management system. Do not remove or alter the original meaning of the user's text. Your output will replace the user's original text. If the input is not narrative text to extend, respond with '-'. Do not explain, comment, or change formatting. Return ONLY the extended text, in the same language as the input."
	data = {
		"model": "gpt-3.5-turbo",
		"temperature": 0.7,
		"max_tokens": 512,
		"messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]
	}
	response = requests.post(
		"https://api.openai.com/v1/chat/completions",
		headers={"Authorization": f"Bearer {api_key}"},
		json=data
	)
	return response.json()


@frappe.whitelist(allow_guest=False)
def has_openai_api_key():
	key = frappe.db.get_single_value("DLS Settings", "openai_api_key")
	return bool(key)


@frappe.whitelist(allow_guest=True)
def is_certificates_enabled():
	return frappe.db.get_single_value('DLS Settings', 'enable_certificates')


@frappe.whitelist(allow_guest=True)
def is_quizzes_enabled():
	return frappe.db.get_single_value('DLS Settings', 'enable_quizzes')
