# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import ceil


class DLSEnrollment(Document):
	def validate(self):
		self.validate_membership_in_same_batch()
		self.validate_membership_in_different_batch_same_course()

	def on_update(self):
		self.update_program_progress()

	def validate_membership_in_same_batch(self):
		filters = {"member": self.member, "course": self.course, "name": ["!=", self.name]}
		if self.batch_old:
			filters["batch_old"] = self.batch_old
		previous_membership = frappe.db.get_value(
			"DLS Enrollment", filters, fieldname=["member_type", "member"], as_dict=1
		)

		if previous_membership:
			member_name = frappe.db.get_value("User", self.member, "full_name")
			course_title = frappe.db.get_value("DLS Course", self.course, "title")
			frappe.throw(
				_("{0} is already a {1} of the course {2}").format(
					member_name, previous_membership.member_type, course_title
				)
			)

	def validate_membership_in_different_batch_same_course(self):
		"""Ensures that a studnet is only part of one batch."""
		# nothing to worry if the member is not a student
		if self.member_type != "Student":
			return

		course = frappe.db.get_value("DLS Batch Old", self.batch_old, "course")
		memberships = frappe.get_all(
			"DLS Enrollment",
			filters={
				"member": self.member,
				"name": ["!=", self.name],
				"member_type": "Student",
				"course": self.course,
			},
			fields=["batch_old", "member_type", "name"],
		)

		if memberships:
			membership = memberships[0]
			member_name = frappe.db.get_value("User", self.member, "full_name")
			frappe.throw(
				_("{0} is already a Student of {1} course through {2} batch").format(
					member_name, course, membership.batch_old
				)
			)

	def update_program_progress(self):
		programs = frappe.get_all(
			"DLS Program Member", {"member": self.member}, ["parent", "name"]
		)

		for program in programs:
			total_progress = 0
			courses = frappe.get_all(
				"DLS Program Course", {"parent": program.parent}, pluck="course"
			)
			for course in courses:
				progress = frappe.db.get_value(
					"DLS Enrollment", {"course": course, "member": self.member}, "progress"
				)
				progress = progress or 0
				total_progress += progress

			average_progress = ceil(total_progress / len(courses))
			frappe.db.set_value("DLS Program Member", program.name, "progress", average_progress)


@frappe.whitelist()
def create_membership(
	course, batch=None, member=None, member_type="Student", role="Member"
):
	frappe.get_doc(
		{
			"doctype": "DLS Enrollment",
			"batch_old": batch,
			"course": course,
			"role": role,
			"member_type": member_type,
			"member": member or frappe.session.user,
		}
	).save(ignore_permissions=True)
	return "OK"


@frappe.whitelist()
def update_current_membership(batch, course, member):
	all_memberships = frappe.get_all(
		"DLS Enrollment", {"member": member, "course": course}
	)
	for membership in all_memberships:
		frappe.db.set_value("DLS Enrollment", membership.name, "is_current", 0)

	current_membership = frappe.get_all(
		"DLS Enrollment", {"batch_old": batch, "member": member}
	)
	if len(current_membership):
		frappe.db.set_value("DLS Enrollment", current_membership[0].name, "is_current", 1)
