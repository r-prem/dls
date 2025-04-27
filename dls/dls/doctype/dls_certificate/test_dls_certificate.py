# Copyright (c) 2021, FOSS United and Contributors
# See license.txt

import unittest

import frappe
from frappe.utils import add_years, cint, nowdate

from dls.dls.doctype.dls_certificate.dls_certificate import create_certificate
from dls.dls.doctype.dls_course.test_dls_course import new_course


class TestDLSCertificate(unittest.TestCase):
	def test_certificate_creation(self):
		course = new_course(
			"Test Certificate",
			{
				"enable_certification": 1,
			},
		)
		certificate = create_certificate(course.name)

		self.assertEqual(certificate.member, "Administrator")
		self.assertEqual(certificate.course, course.name)
		self.assertEqual(certificate.issue_date, nowdate())

		frappe.db.delete("DLS Certificate", certificate.name)
		frappe.db.delete("DLS Course", course.name)
