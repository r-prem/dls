# Copyright (c) 2021, FOSS United and Contributors
# See license.txt

import unittest

import frappe

from dls.dls.doctype.dls_course.test_dls_course import new_course


class TestDLSExercise(unittest.TestCase):
	def new_exercise(self):
		course = new_course("Test Course")
		member = frappe.get_doc(
			{
				"doctype": "DLS Enrollment",
				"course": course.name,
				"member": frappe.session.user,
			}
		)
		member.insert()
		e = frappe.get_doc(
			{
				"doctype": "DLS Exercise",
				"name": "test-problem",
				"course": course.name,
				"title": "Test Problem",
				"description": "draw a circle",
				"code": "# draw a single cicle",
				"answer": ("# draw a single circle\n" + "circle(100, 100, 50)"),
			}
		)
		e.insert()
		return e

	def test_exercise(self):
		e = self.new_exercise()
		assert e.get_user_submission() is None

	def test_exercise_submission(self):
		e = self.new_exercise()
		submission = e.submit("circle(100, 100, 50)")
		assert submission is not None
		assert submission.exercise == e.name
		assert submission.course == e.course

		user_submission = e.get_user_submission()
		assert user_submission is not None
		assert user_submission.name == submission.name

	def tearDown(self):
		frappe.db.delete("DLS Enrollment")
		frappe.db.delete("Exercise Submission")
		frappe.db.delete("DLS Exercise")
