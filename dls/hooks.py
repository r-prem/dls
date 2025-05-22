from . import __version__ as app_version

app_name = "frappe_dls"
app_title = "DLS"
app_publisher = "Raffael"
app_description = "Frappe DLS App"
app_icon_url = "/assets/dls/images/dls-logo.png"
app_icon_title = "Learning"
app_icon_route = "/dls"
app_color = "grey"
app_email = "raffaelprem@gmail.com"
app_license = "AGPL"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/dls/css/dls.css"
# app_include_js = "/assets/dls/js/dls.js"

# include js, css files in header of web template
web_include_css = "dls.bundle.css"
# web_include_css = "/assets/dls/css/dls.css"
web_include_js = ["website.bundle.js"]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "dls/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "/dls"

# website user home page (by Role)
role_home_page = {
	"Website User": "/dls",
	"System Manager": "/",
	"Moderator": "/dls"
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "dls.install.before_install"
after_install = "dls.install.after_install"
after_sync = "dls.install.after_sync"
before_uninstall = "dls.install.before_uninstall"
setup_wizard_requires = "assets/dls/js/setup_wizard.js"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "dls.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Web Template": "dls.overrides.web_template.CustomWebTemplate",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
		"on_change": [
			"dls.dls.doctype.dls_badge.dls_badge.process_badges",
		]
	},
	"Discussion Reply": {"after_insert": "dls.dls.utils.handle_notifications"},
	"Notification Log": {"on_change": "dls.dls.utils.publish_notifications"},
	"User": {
		"validate": "dls.dls.user.validate_username_duplicates",
		"after_insert": "dls.dls.user.after_insert",
	},
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"hourly": [
		"dls.dls.doctype.dls_certificate_request.dls_certificate_request.schedule_evals",
		"dls.dls.api.update_course_statistics",
		"dls.dls.doctype.dls_certificate_request.dls_certificate_request.mark_eval_as_completed",
	],
	"daily": [
		"dls.job.doctype.job_opportunity.job_opportunity.update_job_openings",
		"dls.dls.doctype.dls_payment.dls_payment.send_payment_reminder",
		"dls.dls.doctype.dls_batch.dls_batch.send_batch_start_reminder",
		"dls.dls.doctype.dls_live_class.dls_live_class.send_live_class_reminder",
	],
}

fixtures = ["Custom Field", "Function", "Industry", "dls Category"]

# Testing
# -------

# before_tests = "dls.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	# "frappe.desk.search.get_names_for_mentions": "dls.dls.utils.get_names_for_mentions",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "dls.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Add all simple route rules here
website_route_rules = [
	{"from_route": "/dls/<path:app_path>", "to_route": "dls"},
	{
		"from_route": "/courses/<course_name>/<certificate_id>",
		"to_route": "certificate",
	},
]

website_redirects = [
	{"source": "/", "target": "/dls"},
	{"source": "/update-profile", "target": "/edit-profile"},
	{"source": "/courses", "target": "/dls/courses"},
	{
		"source": r"^/courses/.*$",
		"target": "/dls/courses",
	},
	{"source": "/batches", "target": "/dls/batches"},
	{
		"source": r"/batches/(.*)",
		"target": "/dls/batches",
		"match_with_query_string": True,
	},
	{"source": "/job-openings", "target": "/dls/job-openings"},
	{
		"source": r"/job-openings/(.*)",
		"target": "/dls/job-openings",
		"match_with_query_string": True,
	},
	{"source": "/statistics", "target": "/dls/statistics"},
]

update_website_context = [
	"dls.widgets.update_website_context",
]

jinja = {
	"methods": [
		"dls.dls.utils.get_signup_optin_checks",
		"dls.dls.utils.get_tags",
		"dls.dls.utils.get_lesson_count",
		"dls.dls.utils.get_instructors",
		"dls.dls.utils.get_lesson_index",
		"dls.dls.utils.get_lesson_url",
		"dls.page_renderers.get_profile_url",
		"dls.dls.utils.is_instructor",
		"dls.dls.utils.get_palette",
	],
	"filters": [],
}
## Specify the additional tabs to be included in the user profile page.
## Each entry must be a subclass of dls.dls.plugins.ProfileTab
# profile_tabs = []

## Specify the extension to be used to control what scripts and stylesheets
## to be included in lesson pages. The specified value must be be a
## subclass of dls.plugins.PageExtension
# dls_lesson_page_extension = None

# dls_lesson_page_extensions = [
# 	"dls.plugins.LiveCodeExtension"
# ]

has_website_permission = {
	"dls Certificate Evaluation": "dls.dls.doctype.dls_certificate_evaluation.dls_certificate_evaluation.has_website_permission",
	"dls Certificate": "dls.dls.doctype.dls_certificate.dls_certificate.has_website_permission",
}

## Markdown Macros for Lessons
dls_markdown_macro_renderers = {
	"Exercise": "dls.plugins.exercise_renderer",
	"Quiz": "dls.plugins.quiz_renderer",
	"YouTubeVideo": "dls.plugins.youtube_video_renderer",
	"Video": "dls.plugins.video_renderer",
	"Assignment": "dls.plugins.assignment_renderer",
	"Embed": "dls.plugins.embed_renderer",
	"Audio": "dls.plugins.audio_renderer",
	"PDF": "dls.plugins.pdf_renderer",
}

# page_renderer to manage profile pages
page_renderer = [
	"dls.page_renderers.ProfileRedirectPage",
	"dls.page_renderers.ProfilePage",
	"dls.page_renderers.SCORMRenderer",
]

# set this to "/" to have profiles on the top-level
profile_url_prefix = "/users/"

signup_form_template = "dls.plugins.show_custom_signup"

on_login = "dls.dls.user.on_login"

add_to_apps_screen = [
	{
		"name": "dls",
		"logo": "/assets/dls/frontend/learning.svg",
		"title": "Learning",
		"route": "/dls",
		"has_permission": "dls.dls.api.check_app_permission",
	}
]
