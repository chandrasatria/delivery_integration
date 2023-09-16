# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "delivery_integration"
app_title = "Delivery Integration"
app_publisher = "DAS"
app_description = "App for Manage Third Party of Delivery Method"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "digitalasiasolusindo.developer@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/delivery_integration/css/delivery_integration.css"
# app_include_js = "/assets/delivery_integration/js/delivery_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/delivery_integration/css/delivery_integration.css"
# web_include_js = "/assets/delivery_integration/js/delivery_integration.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

fixtures = [
	# {
	# 	"dt"		: "Delivery Method"
	# },
	# {
	# 	"dt"		: "Delivery Area"
	# },
		# {
		# 	"dt"		: "API Request",
		# 	"filters"	: [
		# 		["document", "in", ["Delivery Method", "Delivery Area"]]
		# 		]
		# }
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "delivery_integration.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "delivery_integration.install.before_install"
# after_install = "delivery_integration.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "delivery_integration.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Territory": {
		"on_update" : "delivery_integration.doctype_function.territory.on_update",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"delivery_integration.tasks.all"
# 	],
# 	"daily": [
# 		"delivery_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"delivery_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"delivery_integration.tasks.weekly"
# 	]
# 	"monthly": [
# 		"delivery_integration.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "delivery_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "delivery_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "delivery_integration.task.get_dashboard_data"
# }

