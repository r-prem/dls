from venv import create

import frappe

from dls.install import create_moderator_role


def execute():
	create_moderator_role()
