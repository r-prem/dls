import frappe
from dls.dls.api import update_course_statistics


def execute():
	update_course_statistics()
